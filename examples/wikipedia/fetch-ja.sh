#!/usr/bin/env bash
# Fetch Japanese Wikipedia introductions and generate .concept files.
# Requires: curl, python3, concept-embed (with OPENAI_API_KEY set)
#
# Usage: cd examples/wikipedia && bash fetch-ja.sh
#
# Data source: Japanese Wikipedia (CC BY-SA 3.0)
# https://ja.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EMBED="$REPO_ROOT/cli/concept-embed"
OUTDIR="$SCRIPT_DIR/concepts"

mkdir -p "$OUTDIR"

# Japanese Wikipedia article titles matching the English set.
# Format: "WikipediaTitle|ConceptName"
# ConceptName is used for the .concept filename and label.
WORDS=(
  # Animals / 動物
  "イヌ|イヌ"
  "ネコ|ネコ"
  "ゾウ|ゾウ"
  "クジラ|クジラ"
  "ワシ|ワシ"
  # Musical instruments / 楽器
  "ピアノ|ピアノ"
  "ギター|ギター"
  "ヴァイオリン|ヴァイオリン"
  "ドラムセット|ドラム"
  "フルート|フルート"
  # Celestial bodies / 天体
  "太陽|太陽"
  "月|月"
  "火星|火星"
  "木星|木星"
  "銀河|銀河"
  # Food / 食べ物
  "寿司|寿司"
  "パスタ|パスタ"
  "カレー|カレー"
  "パン|パン"
  "チョコレート|チョコレート"
  # Programming languages / プログラミング言語
  "Python|Python_ja"
  "JavaScript|JavaScript_ja"
  "Rust (プログラミング言語)|Rust_ja"
  "Go (プログラミング言語)|Go_ja"
  "Haskell|Haskell_ja"
)

for entry in "${WORDS[@]}"; do
  wiki_title="${entry%%|*}"
  concept_name="${entry##*|}"
  outfile="$OUTDIR/${concept_name}.concept"

  if [ -f "$outfile" ]; then
    echo "Skip: $concept_name (already exists)"
    continue
  fi

  echo "Fetching: $wiki_title"

  # Fetch intro text from Japanese Wikipedia API
  encoded=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$wiki_title")
  text=$(curl -s "https://ja.wikipedia.org/api/rest_v1/page/summary/${encoded}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('extract',''))")

  if [ -z "$text" ]; then
    echo "  Warning: no text for $wiki_title, skipping"
    continue
  fi

  echo "$text" | "$EMBED" --name "$concept_name" --language ja \
    --source-url "https://ja.wikipedia.org/wiki/${encoded}" \
    -o "$outfile"

  echo "  -> $outfile"
done

echo ""
echo "Done. Generated $(ls "$OUTDIR"/*.concept 2>/dev/null | wc -l | tr -d ' ') concept files (en + ja)."
echo ""
echo "Try:"
echo "  cli/concept-plot --3d examples/wikipedia/concepts/*.concept -o examples/wikipedia/wikipedia_plot_3d.html"
