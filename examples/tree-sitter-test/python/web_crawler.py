"""A web crawler with rate limiting, retry logic, and result persistence."""

import time
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional, Set, Dict, List, Callable
from urllib.parse import urlparse, urljoin
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of crawling a single URL."""

    url: str
    status_code: int
    content_type: str
    title: Optional[str] = None
    text: Optional[str] = None
    links: List[str] = field(default_factory=list)
    elapsed_ms: float = 0.0
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status_code == 200

    def content_hash(self) -> str:
        """SHA-256 hash of the page text."""
        if self.text is None:
            return ""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


class RateLimiter:
    """Token-bucket rate limiter for polite crawling."""

    def __init__(self, requests_per_second: float = 1.0):
        self.interval = 1.0 / requests_per_second
        self.last_request_time = 0.0

    def wait(self):
        """Block until the next request is allowed."""
        now = time.monotonic()
        elapsed = now - self.last_request_time
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_request_time = time.monotonic()


class RetryPolicy:
    """Configurable retry policy with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute(self, func: Callable, *args, **kwargs):
        """Execute a function with retries."""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (requests.RequestException, ConnectionError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        raise last_exception


class URLFilter:
    """Filter URLs based on domain, path patterns, and seen set."""

    def __init__(self, allowed_domains: Optional[Set[str]] = None,
                 excluded_patterns: Optional[List[str]] = None):
        self.allowed_domains = allowed_domains or set()
        self.excluded_patterns = excluded_patterns or []
        self.seen: Set[str] = set()

    def should_crawl(self, url: str) -> bool:
        """Check if a URL should be crawled."""
        if url in self.seen:
            return False

        parsed = urlparse(url)

        if self.allowed_domains and parsed.netloc not in self.allowed_domains:
            return False

        for pattern in self.excluded_patterns:
            if pattern in parsed.path:
                return False

        return True

    def mark_seen(self, url: str):
        self.seen.add(url)


class ResultStore:
    """Persist crawl results to disk as JSON files."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: CrawlResult):
        """Save a crawl result to a JSON file."""
        import json
        filename = hashlib.md5(result.url.encode()).hexdigest() + ".json"
        filepath = self.output_dir / filename
        data = {
            "url": result.url,
            "status_code": result.status_code,
            "content_type": result.content_type,
            "title": result.title,
            "text_length": len(result.text) if result.text else 0,
            "link_count": len(result.links),
            "elapsed_ms": result.elapsed_ms,
            "content_hash": result.content_hash(),
            "error": result.error,
        }
        filepath.write_text(json.dumps(data, indent=2))

    def load_all(self) -> List[Dict]:
        """Load all saved results."""
        import json
        results = []
        for filepath in self.output_dir.glob("*.json"):
            data = json.loads(filepath.read_text())
            results.append(data)
        return results


class WebCrawler:
    """Main crawler that ties together fetching, filtering, and storage."""

    def __init__(self, rate_limiter: Optional[RateLimiter] = None,
                 retry_policy: Optional[RetryPolicy] = None,
                 url_filter: Optional[URLFilter] = None,
                 result_store: Optional[ResultStore] = None,
                 max_pages: int = 100,
                 timeout: float = 10.0,
                 user_agent: str = "ConceptBot/1.0"):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.retry_policy = retry_policy or RetryPolicy()
        self.url_filter = url_filter or URLFilter()
        self.result_store = result_store
        self.max_pages = max_pages
        self.timeout = timeout
        self.user_agent = user_agent
        self.results: List[CrawlResult] = []

    def fetch_page(self, url: str) -> CrawlResult:
        """Fetch a single page and parse its content."""
        self.rate_limiter.wait()
        start = time.monotonic()

        try:
            response = self.retry_policy.execute(
                requests.get, url,
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent}
            )
            elapsed = (time.monotonic() - start) * 1000

            content_type = response.headers.get("Content-Type", "")
            result = CrawlResult(
                url=url,
                status_code=response.status_code,
                content_type=content_type,
                elapsed_ms=elapsed,
            )

            if response.ok and "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                result.title = soup.title.string if soup.title else None
                result.text = soup.get_text(separator="\n", strip=True)
                result.links = self._extract_links(soup, url)

            return result

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(f"Failed to fetch {url}: {e}")
            return CrawlResult(
                url=url, status_code=0, content_type="",
                elapsed_ms=elapsed, error=str(e)
            )

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract and normalize links from HTML."""
        links = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.append(clean)
        return links

    def crawl(self, start_urls: List[str]) -> List[CrawlResult]:
        """Crawl starting from a list of seed URLs (BFS)."""
        queue = list(start_urls)
        pages_crawled = 0

        while queue and pages_crawled < self.max_pages:
            url = queue.pop(0)
            if not self.url_filter.should_crawl(url):
                continue

            self.url_filter.mark_seen(url)
            logger.info(f"Crawling [{pages_crawled + 1}/{self.max_pages}]: {url}")

            result = self.fetch_page(url)
            self.results.append(result)
            pages_crawled += 1

            if self.result_store:
                self.result_store.save(result)

            if result.is_success:
                for link in result.links:
                    if self.url_filter.should_crawl(link):
                        queue.append(link)

        logger.info(f"Crawl complete: {pages_crawled} pages fetched")
        return self.results

    def get_statistics(self) -> Dict:
        """Return crawl statistics."""
        successful = [r for r in self.results if r.is_success]
        failed = [r for r in self.results if not r.is_success]
        avg_time = sum(r.elapsed_ms for r in self.results) / len(self.results) if self.results else 0
        return {
            "total_pages": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "avg_response_ms": round(avg_time, 1),
            "unique_domains": len(set(urlparse(r.url).netloc for r in self.results)),
        }
