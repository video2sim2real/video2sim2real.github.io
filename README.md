# Paper project page

A single-page academic project website, built on the HTML5 UP **Strata** template
(the same family used by many ML paper pages, e.g. Nerfies / 3D Diffusion Policy).
Everything is static — plain HTML/CSS/JS, no build step.

## Layout

```
site/
├── index.html              ← the whole page (edit this): hero, side menu, sections
├── appendix.pdf            ← the paper's appendix, linked from the page (built by tools/)
├── assets/                 ← template engine — you normally don't touch these
│   ├── main.css            ←   styling (hero background + accent live here)
│   ├── *.js                ←   jQuery + skel responsive framework + helpers
│   └── images/
│       ├── overlay.png     ←   1×1 transparent no-op (kept for the template)
│       └── placeholder.svg ←   the grey "MEDIA PLACEHOLDER" graphic
├── images/                 ← YOUR figures, teaser, favicon, header_bg.jpg
├── tools/
│   ├── serve.py            ←   local preview server (use instead of `python3 -m http.server`)
│   ├── build_appendix_pdf.py ← builds appendix.pdf from the Overleaf source
│   └── appendix_only.tex   ←   the LaTeX wrapper that script compiles
├── videos/                 ← YOUR result videos (.mp4)
├── author_images/          ← YOUR author headshots (optional)
├── .nojekyll               ← tells GitHub Pages to serve files as-is
└── README.md
```

## Customise it

1. Open `index.html` and search for **`EDIT`** — every spot that needs your content
   is flagged with an `<!-- EDIT ... -->` comment. Fill in: title, subtitle, authors
   (+ homepage links and affiliation superscripts), the link buttons, venue, abstract,
   method/results text, and the BibTeX block.
2. **Hero background:** drop an image at `images/header_bg.jpg`. Without one you get a
   clean dark hero (configured in `assets/main.css`, the `header { }` rule — that's also
   where you tune the darkening overlay).
3. **Figures & videos:** put files in `images/` and `videos/`, then replace each
   `placeholder.svg` slot. The exact `<img>` and `<video>` markup to use is shown in the
   comments right next to each slot.
4. **Accent colour:** change `--accent` near the top of `index.html`.
5. **Favicon (optional):** drop a square PNG at `images/favicon.png`.

## Side menu

The fixed menu on the left (a slide-in drawer below ~1180px) is the `<nav id="side-nav">`
block at the top of `<body>` in `index.html`. Each entry is just a link to a section's
`id`, so to add or rename a section, add or rename its `<li>` there — the script that
highlights the current section reads the links itself, nothing else needs updating.

## Appendix (PDF)

The appendix is not on the page itself: the **Appendix** section (and the hero button) link to
`appendix.pdf`, which reviewers can view or download. Build it from the Overleaf source with

```bash
python3 tools/build_appendix_pdf.py      # needs: brew install tectonic mupdf-tools
```

Put a download of the Overleaf project in `paper_overleaf/` first. That folder is git-ignored —
it holds the **de-anonymised** source, so it must never be pushed; the script only reads it and
works in a throw-away copy. What you get is a stand-alone, anonymous PDF:

- title + "Appendix", *Anonymous Authors*, then the appendices in the order `main.tex` lists them;
- **numbering continues from the main paper** (the script compiles the full paper once to find
  where its figures/tables/equations stop — currently the appendix starts at Fig. 5, Table III),
  and references into the main paper read "Table II of the main paper";
- its own reference list, PDF bookmarks, page numbers, and clickable links (figure/table/equation
  references and citation numbers, coloured blue). Note `ieeeconf.cls` deliberately disables
  hyperref's citation links (its fake `\NAT@parse`); the wrapper undoes that, as the class suggests;
- a few typos in the source are patched on the fly (the `FIXES` list at the top of the script —
  fix them on Overleaf and the entries simply stop matching).

The script refuses to write the PDF if it contains `??`, characters that got dropped, or any
author/affiliation name from `main.tex`, and it refreshes the "N pages · X MB" note in
`index.html`. The paper is written for pdfLaTeX; Tectonic is XeTeX-based, which is why
`tools/appendix_only.tex` selects the classic font encoding and maps Unicode dashes/quotes —
read the comments there before changing it.

## Preview locally

From this folder:

```bash
python3 tools/serve.py          # then open http://localhost:8000
python3 tools/serve.py --lan    # ...also reachable from a phone on the same Wi-Fi
```

Use this rather than `python3 -m http.server`. Python's built-in server ignores HTTP range
requests, so Chrome keeps every `<video>` download open and stalled; with ~20 clips on the
page that eats its 6 connections per host, and anything requested afterwards waits forever
(blank images, links that never open) — seeking in a video fails too. `tools/serve.py` answers
range requests like GitHub Pages does, and asks the browser to revalidate files, so a normal
refresh shows your latest edit. For the same reason, don't put `loading="lazy"` on images
further down the page: once the clips start, late requests never get a connection.

## Deploy to GitHub Pages

This folder is already a git repo with an initial commit. Create an empty repo on
GitHub, then:

```bash
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git   # ← your repo
git push -u origin main
```

On GitHub: **Settings → Pages → Build and deployment → Source: “Deploy from a branch”**,
pick **`main` / `(root)`**, Save. It goes live in ~1 minute.

- Repo named `REPO` → served at `https://USERNAME.github.io/REPO/`
- Repo named `USERNAME.github.io` → served at `https://USERNAME.github.io/`

After you know the URL, set `og:url` in `index.html` so link previews work.

### Notes on media size

GitHub caps individual files at **100 MB** and nags above a **~1 GB** repo. Keep videos
short and compressed (e.g. `ffmpeg -i in.mp4 -vcodec libx264 -crf 28 -an out.mp4`). For
anything large, host it externally (YouTube embed, or a release asset) rather than
committing it.

## Credit

Template: [HTML5 UP — Strata](https://html5up.net/strata) (CCA 3.0). The attribution link
in the page's *Acknowledgements* section satisfies the license — please keep it, or buy a
license from HTML5 UP to remove it.
