"""Visualize .concept embeddings as an interactive 2D/3D scatter plot using UMAP."""

import argparse
import os
import signal
import sys
import tempfile
from pathlib import Path

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

# Use a per-process numba cache directory to avoid lock conflicts in parallel execution
os.environ["NUMBA_CACHE_DIR"] = tempfile.mkdtemp(prefix="numba_cache_")

import numpy as np
import umap
import plotly.graph_objects as go

from concept_file import read_concept


def load_concepts(paths):
    """Load .concept files from a list of paths. Return (names, texts, full_texts, embeddings, paths)."""
    names = []
    texts = []
    full_texts = []
    embeddings = []
    file_paths = []
    for p in paths:
        p = p.strip()
        if not p:
            continue
        try:
            data = read_concept(p)
            vec = data.get("embedding", {}).get("vector")
            if not vec:
                print(f"Warning: {p} has no embedding, skipping", file=sys.stderr)
                continue
            names.append(data.get("concept", Path(p).stem))
            text = data.get("text", "")
            full_texts.append(text)
            if len(text) > 200:
                text = text[:200] + "..."
            texts.append(text)
            embeddings.append(vec)
            file_paths.append(p)
        except (ValueError, FileNotFoundError) as e:
            print(f"Warning: {p}: {e}", file=sys.stderr)
    return names, texts, full_texts, np.array(embeddings), file_paths


def main():
    parser = argparse.ArgumentParser(
        description="Visualize .concept embeddings as a 2D/3D scatter plot using UMAP"
    )
    parser.add_argument(
        "files", nargs="*",
        help="Paths to .concept files (also reads from stdin if piped)"
    )
    parser.add_argument(
        "-o", "--output", default="concept_plot.html",
        help="Output HTML file path (default: concept_plot.html)"
    )
    parser.add_argument(
        "--n-neighbors", type=int, default=15,
        help="UMAP n_neighbors parameter (default: 15)"
    )
    parser.add_argument(
        "--min-dist", type=float, default=0.1,
        help="UMAP min_dist parameter (default: 0.1)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--3d", dest="three_d", action="store_true",
        help="Generate a 3D scatter plot instead of 2D"
    )
    args = parser.parse_args()

    # Collect file paths from arguments and stdin
    paths = list(args.files)
    if not sys.stdin.isatty():
        paths.extend(sys.stdin.read().splitlines())

    if not paths:
        print("Error: no .concept files specified", file=sys.stderr)
        print("Usage: concept-plot file1.concept file2.concept ...", file=sys.stderr)
        print("       find . -name '*.concept' | concept-plot", file=sys.stderr)
        sys.exit(1)

    names, texts, full_texts, embeddings, file_paths = load_concepts(paths)

    if len(names) < 2:
        print("Error: need at least 2 .concept files with embeddings", file=sys.stderr)
        sys.exit(1)

    n_components = 3 if args.three_d else 2
    print(f"Loaded {len(names)} concepts, running UMAP ({n_components}D)...", file=sys.stderr)

    # Adjust n_neighbors if fewer data points
    n_neighbors = min(args.n_neighbors, len(names) - 1)

    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=args.min_dist,
        n_epochs=50,
        random_state=args.seed,
    )
    coords = reducer.fit_transform(embeddings)

    # Build hover text: concept name + truncated text
    import html
    hover_texts = []
    for name, text, fp in zip(names, texts, file_paths):
        hover = f"<b>{html.escape(name)}</b><br>{html.escape(fp)}<br><br>{html.escape(text)}"
        hover_texts.append(hover)

    # Compute colors from UMAP coordinates so nearby points share similar colors.
    # For 3D: normalize (x, y, z) to [0, 1] and map to RGB.
    # For 2D: use angle from centroid for hue, distance for saturation.
    def coords_to_colors(coords):
        import colorsys
        if coords.shape[1] == 3:
            mins = coords.min(axis=0)
            maxs = coords.max(axis=0)
            ranges = maxs - mins
            ranges[ranges == 0] = 1.0
            normed = (coords - mins) / ranges
            colors = [
                f"rgb({int(r*255)},{int(g*255)},{int(b*255)})"
                for r, g, b in normed
            ]
        else:
            cx, cy = coords[:, 0].mean(), coords[:, 1].mean()
            dx = coords[:, 0] - cx
            dy = coords[:, 1] - cy
            angles = np.arctan2(dy, dx)
            hues = (angles + np.pi) / (2 * np.pi)  # [0, 1]
            dists = np.sqrt(dx**2 + dy**2)
            max_dist = dists.max() if dists.max() > 0 else 1.0
            sats = 0.4 + 0.6 * (dists / max_dist)  # [0.4, 1.0]
            colors = []
            for h, s in zip(hues, sats):
                r, g, b = colorsys.hls_to_rgb(h, 0.5, s)
                colors.append(f"rgb({int(r*255)},{int(g*255)},{int(b*255)})")
        return colors

    point_colors = coords_to_colors(coords)

    if args.three_d:
        fig = go.Figure(data=go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode="markers+text",
            text=names,
            textfont=dict(size=9),
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(size=5, color=point_colors, opacity=0.8),
        ))
        fig.update_layout(
            title="Concept Embedding Map (3D)",
            scene=dict(
                xaxis_title="UMAP-1",
                yaxis_title="UMAP-2",
                zaxis_title="UMAP-3",
            ),
            template="plotly_white",
            hoverlabel=dict(bgcolor="white", font_size=12),
            width=1000,
            height=800,
        )
    else:
        fig = go.Figure(data=go.Scatter(
            x=coords[:, 0],
            y=coords[:, 1],
            mode="markers+text",
            text=names,
            textposition="top center",
            textfont=dict(size=11),
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(size=10, color=point_colors, opacity=0.8),
        ))
        fig.update_layout(
            title="Concept Embedding Map",
            xaxis_title="UMAP-1",
            yaxis_title="UMAP-2",
            template="plotly_white",
            hoverlabel=dict(bgcolor="white", font_size=12),
            width=1000,
            height=700,
        )

    # Write HTML with search functionality
    plot_html = fig.to_html(include_plotlyjs=True, full_html=True)

    # Inject search UI and JavaScript before closing </body>
    search_js = """
<div id="search-container" style="position:fixed;top:10px;left:10px;z-index:1000;background:white;padding:10px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.2);font-family:sans-serif;">
  <input id="search-input" type="text" placeholder="Search concepts..." style="width:250px;padding:6px 10px;border:1px solid #ccc;border-radius:4px;font-size:14px;">
  <span id="search-count" style="margin-left:8px;color:#666;font-size:12px;"></span>
  <button id="search-clear" onclick="clearSearch()" style="margin-left:4px;padding:4px 8px;border:1px solid #ccc;border-radius:4px;background:#f5f5f5;cursor:pointer;font-size:12px;">Clear</button>
</div>
<script>
(function() {
  var names = NAMES_JSON;
  var fullTexts = TEXTS_JSON;
  var plotDiv = document.getElementsByClassName('plotly-graph-div')[0];

  function doSearch() {
    var query = document.getElementById('search-input').value.toLowerCase().trim();
    var countEl = document.getElementById('search-count');
    if (!query) {
      clearSearch();
      return;
    }
    var sizes = [];
    var opacities = [];
    var matchCount = 0;
    for (var i = 0; i < names.length; i++) {
      if (names[i].toLowerCase().indexOf(query) !== -1 || fullTexts[i].toLowerCase().indexOf(query) !== -1) {
        sizes.push(MATCH_SIZE);
        opacities.push(1.0);
        matchCount++;
      } else {
        sizes.push(DIM_SIZE);
        opacities.push(0.15);
      }
    }
    Plotly.restyle(plotDiv, {'marker.size': [sizes], 'marker.opacity': [opacities]}, [0]);
    countEl.textContent = matchCount + ' / ' + names.length;
  }

  window.clearSearch = function() {
    document.getElementById('search-input').value = '';
    document.getElementById('search-count').textContent = '';
    var sizes = new Array(names.length).fill(DEFAULT_SIZE);
    var opacities = new Array(names.length).fill(0.8);
    Plotly.restyle(plotDiv, {'marker.size': [sizes], 'marker.opacity': [opacities]}, [0]);
  };

  document.getElementById('search-input').addEventListener('input', doSearch);
})();
</script>
"""
    # Set marker sizes based on 2D/3D
    if args.three_d:
        search_js = search_js.replace("MATCH_SIZE", "12").replace("DIM_SIZE", "3").replace("DEFAULT_SIZE", "5")
    else:
        search_js = search_js.replace("MATCH_SIZE", "18").replace("DIM_SIZE", "5").replace("DEFAULT_SIZE", "10")

    import json
    import base64
    # Encode as base64 to avoid </script> and other HTML-breaking characters in JSON
    names_b64 = base64.b64encode(json.dumps(names, ensure_ascii=False).encode("utf-8")).decode("ascii")
    texts_b64 = base64.b64encode(json.dumps(full_texts, ensure_ascii=False).encode("utf-8")).decode("ascii")
    search_js = search_js.replace("NAMES_JSON", f"JSON.parse(atob('{names_b64}'))")
    search_js = search_js.replace("TEXTS_JSON", f"JSON.parse(atob('{texts_b64}'))")

    plot_html = plot_html.replace("</body>", search_js + "</body>")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(plot_html)
    print(f"Plot saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
