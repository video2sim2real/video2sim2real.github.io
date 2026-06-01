# Paper project page

A single-page academic project website, built on the HTML5 UP **Strata** template
(the same family used by many ML paper pages, e.g. Nerfies / 3D Diffusion Policy).
Everything is static — plain HTML/CSS/JS, no build step.

## Layout

```
site/
├── index.html              ← the whole page (edit this)
├── assets/                 ← template engine — you normally don't touch these
│   ├── main.css            ←   styling (hero background + accent live here)
│   ├── *.js                ←   jQuery + skel responsive framework + helpers
│   └── images/
│       ├── overlay.png     ←   1×1 transparent no-op (kept for the template)
│       └── placeholder.svg ←   the grey "MEDIA PLACEHOLDER" graphic
├── images/                 ← YOUR figures, teaser, favicon, header_bg.jpg
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

## Preview locally

From this folder:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

(Any static file server works; opening `index.html` directly via `file://` also mostly
works but a server matches how GitHub Pages serves it.)

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
