# Working notes for Claude

README.md is the reference for what this site is and how it was built; read it first. These are the operational rules.

## Build and preview

- `python3 tools/build.py` regenerates `site/index.html` and `site/about/index.html` from `_reference/capture/`. Needs `beautifulsoup4` (not installed system-wide; use a venv). Never hand-edit the generated HTML; change `tools/build.py` and rebuild.
- Links are root-relative clean URLs, so pages don't work from `file://`. Preview with `python3 -m http.server -d site` or `vercel dev` in `site/`.
- `python3 tools/logo.py` regenerates `logo/`; `python3 tools/favicons.py` regenerates the favicons in `site/`. Both rasterize with Playwright's `chrome-headless-shell` (or `CHROME=`). `logo.py` itself is dependency-free.
- The mark's geometry is final as of 2026-10-04 (`arcs=3`, `kink_ratio=2.2`, `roundover=0.12`, `aspect=0.62`, `fill=0.8`). Don't change defaults without being asked; show variants side by side in the browser instead.

## Deploy

- A push to `main` that touches `site/**` deploys to **production** (eisenbraunelectric.co) via `.github/workflows/deploy.yml`. Other branches get previews. Ask before pushing site changes to `main`.
- Vercel's Git integration is intentionally not connected (see README "Deploy"); don't try to connect it.

## Git

- Remote is HTTPS (`https://github.com/h-gf-sh/eisenbraunelectric.git`). Identity and credentials come from a per-folder git config on this machine (see `~/projects/personal/CLAUDE.md`); check `git config user.email` before the first commit in a session.
- Don't run `gh auth login`/`gh auth switch` or change global git config for this repo: `gh`'s active account is a different one that other projects depend on.
- `RUNBOOK-github-accounts.md` is local only (gitignored) and must stay out of the repo.
