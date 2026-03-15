#!/usr/bin/env bash
# Fetch Wikipedia introductions and generate .concept files.
# Requires: curl, python3, concept-embed (with OPENAI_API_KEY set)
#
# Usage: cd examples/wikipedia && bash fetch.sh
#
# Data source: English Wikipedia (CC BY-SA 3.0)
# https://en.wikipedia.org/wiki/Wikipedia:Text_of_the_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EMBED="$REPO_ROOT/cli/concept-embed"
OUTDIR="$SCRIPT_DIR/concepts"

mkdir -p "$OUTDIR"

# Words grouped by category for clear clustering
WORDS=(
  # Animals
  Dog Cat Elephant Whale Eagle
  # Musical instruments
  Piano Guitar Violin Drum Flute
  # Celestial bodies
  Sun Moon Mars Jupiter Galaxy
  # Food
  Sushi Pasta Curry Bread Chocolate
  # Programming languages
  "Python (programming language)"
  "JavaScript"
  "Rust (programming language)"
  "Go (programming language)"
  "Haskell (programming language)"
)

# Clean concept name: remove parenthetical qualifiers
clean_name() {
  echo "$1" | sed 's/ *(.*//'
}

for word in "${WORDS[@]}"; do
  name=$(clean_name "$word")
  safe=$(echo "$name" | tr ' ' '_')
  outfile="$OUTDIR/${safe}.concept"

  if [ -f "$outfile" ]; then
    echo "Skip: $name (already exists)"
    continue
  fi

  echo "Fetching: $word"

  # Fetch intro text from Wikipedia API
  encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$word'))")
  text=$(curl -s "https://en.wikipedia.org/api/rest_v1/page/summary/${encoded}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('extract',''))")

  if [ -z "$text" ]; then
    echo "  Warning: no text for $word, skipping"
    continue
  fi

  echo "$text" | "$EMBED" --name "$name" --language en \
    --source-url "https://en.wikipedia.org/wiki/${encoded}" \
    -o "$outfile"

  echo "  -> $outfile"
done

echo ""
echo "Done. Generated $(ls "$OUTDIR"/*.concept 2>/dev/null | wc -l | tr -d ' ') concept files."
echo ""
echo "Try:"
echo "  cli/concept-plot --3d examples/wikipedia/concepts/*.concept -o examples/wikipedia/wikipedia_plot_3d.html"
