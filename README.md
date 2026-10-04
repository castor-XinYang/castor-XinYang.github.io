# castor-xinyang.github.io

Personal website of Xin (Castor) Yang, built with [Quarto](https://quarto.org)
and deployed to GitHub Pages by `.github/workflows/publish.yml` on every push to `main`.

## Local preview

```sh
quarto preview
```

## Common edits

| What | Where |
|------|-------|
| About, News, Experience, Education | `index.qmd` |
| Research interests | `research.qmd` |
| Publications | edit `publications/publications.bib`, then run `python3 scripts/build_publications.py` |
| Paper summary / figure (optional) | `publications/<bibkey>.md`, `publications/<bibkey>.png` |
| Software | `software.qmd` |
| CV / Resume | replace the PDFs in `cv/` (keep the file names) |
| Navbar, social links, footer | `_quarto.yml` |
| Colors and fonts | `theme.scss`, `styles.css` |
| Analytics | `header.html` (Cloudflare token) |

## Hidden pages

`blog.qmd` (posts in `posts/`) and `travel.qmd` are drafts: they are not
rendered or linked. To publish one, set `draft: false` in its front matter
and uncomment its entry in the navbar in `_quarto.yml`.

## TODO

- [ ] Google Scholar link (`_quarto.yml`, commented out)
- [ ] Cloudflare Web Analytics token (`header.html`)
- [ ] mhmmbeta GitHub link (`software.qmd`)
