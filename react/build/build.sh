#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Building Modern React 19: The Complete Guide..."

# Collect all chapter markdown files in order
CHAPTERS=""
CHAPTERS="$CHAPTERS manuscript/00-front-matter/preface.md"
for i in $(seq -w 1 29); do
  dir=$(find manuscript -maxdepth 1 -type d -name "${i}-*" | head -1)
  if [ -n "$dir" ] && [ -f "$dir/chapter.md" ]; then
    CHAPTERS="$CHAPTERS $dir/chapter.md"
  fi
done
CHAPTERS="$CHAPTERS manuscript/99-back-matter/appendix-a.md"
CHAPTERS="$CHAPTERS manuscript/99-back-matter/appendix-b.md"

echo "Chapters found:"
echo "$CHAPTERS" | tr ' ' '\n' | grep -v '^$'

mkdir -p build/output

pandoc \
  --metadata-file=manuscript/metadata.yaml \
  --pdf-engine=xelatex \
  --top-level-division=chapter \
  --number-sections \
  --toc \
  --toc-depth=2 \
  --highlight-style=kate \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=blue \
  -o build/output/modern-react-19-complete-guide.pdf \
  $CHAPTERS

echo ""
echo "PDF generated successfully!"
echo "Output: build/output/modern-react-19-complete-guide.pdf"
PAGE_COUNT=$(python3 -c "
import subprocess
result = subprocess.run(['mdls', '-name', 'kMDItemNumberOfPages', 'build/output/modern-react-19-complete-guide.pdf'], capture_output=True, text=True)
print(result.stdout.strip().split('=')[-1].strip())
" 2>/dev/null || echo "unknown")
echo "Pages: $PAGE_COUNT"
