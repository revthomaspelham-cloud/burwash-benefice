# Notes for AI assistants

This repo is the website of the Benefice of Burwash, Burwash Weald & Etchingham
(three Church of England parishes in East Sussex): https://burwashbenefice.org.uk.
The Rector, Revd Tom Pelham, owns it. Read README.md for the human editing guide;
this file covers what an assistant needs to know before making changes.

## Architecture

- A static site built by one script, `build.py` (Python 3; the only dependency is `markdown`).
- `python3 build.py` reads `src/` and writes the complete site into `docs/`.
  GitHub Pages serves `main` / `docs`. `docs/CNAME` is written by the build.
- `.github/workflows/build.yml` runs the build on every push touching `src/**` or
  `build.py`, and daily at 03:15 UTC (so expired news drops off), and commits `docs/`.
  Still commit a locally built `docs/` with your change, so the site updates even
  if Actions is slow.
- `docs/` is generated. Never hand-edit it.

## Content files

Every page and news file has a header of `key: value` lines, then a line `---`,
then the body.

### Pages: `src/pages/*.md` or `*.html`

Each file becomes `docs/<name>.html`. Header keys:

| key | meaning |
|---|---|
| `title` | `<title>` and default `<h1>` |
| `nav` | key of the menu item to highlight (matches the 3rd field in `NAV`) |
| `description` | meta description |
| `heading` | optional `<h1>` if it differs from `title` |
| `intro` | optional line under the `<h1>` |
| `layout` | `.md` only: `prose` (default) or `raw` |

- `.md` bodies are converted with Python-Markdown (`extra`, `sane_lists`), so raw
  HTML blocks such as `<div class="facts">` are allowed inside them.
- In a `.md` page with `layout: prose` (the default), the body is wrapped in the
  standard page head (h1 + intro) and a narrow `.prose` column, so simple pages are
  pure text. Use `layout: raw` for a Markdown page that writes its own sections.
- `.html` bodies are used exactly as written. Pages with complex layouts (index,
  services, church pages, contact, give, get-involved, choir, bellringing) are
  `.html` and contain their own `<div class="page-head">` and `<section>`s.
- Files whose names start with `_` are skipped.

### News: `src/news/YYYY-MM-DD-slug.md` (or `.html`)

Each file becomes `docs/news-<stem>.html` and appears on `news.html` and the home page.

| key | meaning |
|---|---|
| `title`, `date` (ISO), `summary` | required |
| `image` | optional, path under `images/` |
| `until` | optional last day shown (ISO). Past items are dropped at build time, and client-side JS also removes any `[data-until]` element once the date has passed |
| `headline` | optional ONE short sentence (~10 words) shown in the rotating `.news-bar` on the home page (`<!--NEWS_BAR-->` placeholder). It must be a summary, never the body text. Items without one are left off the bar |

`src/news/_template.md` is the copy-me template.

### Settings: `src/settings.txt`

`key: value` lines (`#` comments allowed). Any `{{key}}` in any page or news file
(header or body) is replaced at build time. Current keys: `rector_name`,
`rector_email`, `rector_phone`, `rector_phone_link`, `whatsapp_link`,
`facebook_link`. Use these placeholders rather than hard-coding contact details.

### Other configuration in `build.py`

- `NAV`: the menu as `(label, href, key, children)`.
- `REDIRECTS`: old website-builder paths to new pages (stub pages are generated).
- `THEME = "mix"` selects `src/theme-mix.css` on top of `src/style.css`.
- Footer JS: rotates `.news-bar .nb-item` every 6s (pauses on hover/focus,
  respects reduced motion) and removes expired `[data-until]` elements.

## Checking a change

```
pip install markdown
python3 build.py
cd docs && python3 -m http.server 8765
```

For a refactor with no intended visual change, copy `docs/` before and diff after
(`diff -rq`). Look at changed pages at both desktop and phone widths
(headless Chrome screenshots work).

## House style

- British English. Warm, plain and welcoming. Short sentences. No jargon.
- Many readers are elderly. Don't call online routes "easier" or "more
  accessible": paper and in-person options stay available.
- Families and children are welcome at all services. Don't single out noise.
- Church names: "St Bartholomew's, Burwash", "St Philip's, Burwash Weald",
  "Etchingham" (in full: The Assumption of the Blessed Virgin & St Nicholas, Etchingham).
- Times are written like `10.30am` and `4.30pm`. Dates like "Sunday 6 December".
- The service calendar is a Google Calendar embed at `services.html#calendar`.
  Link there for "services this week".

## Working conventions

- **Discuss changes with Tom before making them**, unless he has asked for that
  specific change. Show drafts of anything sent in his name before creating them.
- **The repo is public.** Nothing private goes in it: no personal emails other than
  the Rector's public address, no spreadsheet or form-admin links, no drafts.
- `src/drafts/` is gitignored and is for unpublished pages (it builds locally only
  when moved into `src/pages/`).
- Commit messages: short imperative summary. Pull/rebase before pushing
  (`git pull --rebase origin main`), because the Action also commits.

## Pending, awaiting decisions by others

- **Privacy / data protection section.** A privacy notice page (general notice, an
  electoral roll notice at `#electoral-roll`, and a retention table at `#retention`),
  a photo-consent form and an electoral roll form are prepared but **must not be
  published until all three PCCs approve**. When approved, the plan is to move
  `privacy.html` into `src/pages/`, add "Privacy & photo consent" under
  Safeguarding in `NAV`, and add "Join the electoral roll" to Get involved.
  The drafts are not in this repo; ask Tom.
- Christmas Eve and Christmas Day service times are still to be added when supplied.
- Parish safeguarding officers may be added to the contact form once they agree.

## Related things outside this repo

- A weekly scheduled assistant task (Mondays, 07:45 UK time) suggests news items
  from Tom's email and calendar. It only suggests; nothing is published without Tom.
- The benefice Google account (St Bartholomew's) owns the service calendar and the
  forms. It is a shared benefice account and is **not** used for correspondence.
