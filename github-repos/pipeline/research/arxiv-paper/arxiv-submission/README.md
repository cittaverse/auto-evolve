# arXiv Submission Package

## Contents
- `main.tex` — Paper source (paper-v1.1.tex)
- `references.bib` — BibTeX references (52 entries)
- `arxiv.sty` — Minimal arXiv style file
- `cover-letter.md` — Submission cover letter
- `figures/` — Figure directory (add figures here)

## Compile
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Submission Checklist
- [ ] Compile locally with pdflatex (or upload to Overleaf)
- [ ] Verify all references resolve
- [ ] Upload to arxiv.org as cs.HC (primary) + cs.CL (cross-list)
- [ ] Set metadata: title, authors, abstract, categories
