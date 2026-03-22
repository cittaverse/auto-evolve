#!/bin/bash
# Compile arXiv paper PDF
# Usage: ./compile.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Compiling arXiv Paper ==="
echo "Working directory: $SCRIPT_DIR"

# Check for required files
if [ ! -f "main.tex" ]; then
    echo "ERROR: main.tex not found"
    exit 1
fi

if [ ! -f "references.bib" ]; then
    echo "ERROR: references.bib not found"
    exit 1
fi

# Check for pdflatex
if ! command -v pdflatex &> /dev/null; then
    echo "WARNING: pdflatex not found. Installing texlive..."
    # Uncomment below to auto-install (requires sudo)
    # sudo apt-get update && sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-bibtex-extra
    echo "Please install TeX Live manually:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-extra texlive-bibtex-extra"
    echo "  macOS: brew install --cask mactex"
    exit 1
fi

# Compile (run twice for references)
echo "Running pdflatex (1/2)..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1

echo "Running bibtex..."
bibtex main > /dev/null 2>&1

echo "Running pdflatex (2/2)..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1

echo "Running pdflatex (3/2 for final refs)..."
pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1

# Check output
if [ -f "main.pdf" ]; then
    echo "=== Compilation Successful ==="
    echo "Output: $SCRIPT_DIR/main.pdf"
    echo "File size: $(ls -lh main.pdf | awk '{print $5}')"
    echo ""
    echo "Next steps:"
    echo "  1. Review main.pdf for formatting issues"
    echo "  2. Submit to arXiv: https://arxiv.org/submit"
    echo "  3. Category: cs.CL (Computation and Language) or cs.HC (Human-Computer Interaction)"
else
    echo "ERROR: Compilation failed. Check main.log for details."
    exit 1
fi

# Cleanup auxiliary files
echo ""
echo "Cleaning up auxiliary files..."
rm -f main.aux main.bbl main.blg main.log main.out main.nav main.snf main.snt main.toc main.vrb 2>/dev/null || true

echo "Done!"
