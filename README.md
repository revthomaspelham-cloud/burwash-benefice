# Burwash Benefice website

The website for the Benefice of Burwash, Burwash Weald & Etchingham:
https://burwashbenefice.org.uk

This page explains how to change the website by hand. If you're an AI assistant
helping with the site, read [AGENTS.md](AGENTS.md) as well.

## The short version

- Everything you edit lives in **`src/`**.
- **`docs/`** is the finished website. It's generated automatically, so never edit it by hand.
- When you save a change to `src/` on GitHub, the site rebuilds itself within a
  couple of minutes (see the **Actions** tab to watch it happen).

## Editing on the GitHub website (no software needed)

1. Go to the file in `src/`, e.g. `src/pages/weddings.md`.
2. Click the pencil icon (**Edit this file**).
3. Make your change, then click **Commit changes…** and **Commit changes** again.
4. Wait two or three minutes and refresh the website.

To add a file (e.g. a news item), open the folder and use **Add file → Create new file**.
To add a photo, open `src/images/` and use **Add file → Upload files**.

## Common jobs

### Add a news item

1. Open `src/news/` and look at `_template.md`.
2. Create a new file named like `2026-12-01-carol-service.md` (date first, then a short
   name with dashes, no spaces).
3. Copy the template into it and fill it in:

```
title: Carol service at St Philip's
date: 2026-12-01
summary: Join us for candlelit carols on Sunday 20 December at 6pm.
image: images/weald-snow.jpg
until: 2026-12-20
headline: Candlelit carols at St Philip's, Sunday 20 December.
---
The story itself goes here, in plain text.

Leave a blank line between paragraphs. **Bold** looks like this,
and links look like [this](services.html).
```

| Line | What it does |
|---|---|
| `title` | The heading of the news item |
| `date` | The date it was posted (YYYY-MM-DD). Newest shows first. |
| `summary` | One or two sentences for the news list and home page |
| `image` | A photo from `src/images/` (optional) |
| `until` | The last day it should appear. After that it disappears from the site automatically. Leave it out for news that never expires. |
| `headline` | One short sentence (about 10 words) for the rotating bar at the top of the home page. Leave it out to keep the item off the bar. |

The `---` line separates the details from the story. Don't remove it.

To take a news item down early, delete its file (or change `until` to yesterday).

### Change the Rector's phone, email, WhatsApp or Facebook link

Edit **`src/settings.txt`**. The new details appear everywhere on the site.
In page files these appear as `{{rector_email}}`, `{{rector_phone}}` and so on.

The early Sunday service time is there too (`early_time`). A line such as
`early_time from 2026-12-28: 9.15am` makes a change happen automatically on that date.

Evening service times (`{{evening_time}}`) switch between 4.30pm and 6pm by
themselves when the clocks change.

### Change the words on a page

Pages are in `src/pages/`. There are two kinds:

- **`.md` files** (baptism, weddings, funerals, about, safeguarding) are plain text and the
  easiest to edit. The lines above `---` are the page title, the line under the
  heading (`intro`), and the description shown in Google.
  - `## Heading` makes a heading, `### Smaller heading` a smaller one.
  - `- item` makes a bullet list.
  - `**bold**`, `[link text](page.html)`.
  - Some boxes are written in HTML (lines starting with `<`). Edit the words between
    the tags and leave the tags alone.
- **`.html` files** (home page, services, church pages, contact…) have more complex
  layouts. You can still change the words: find the sentence and edit it, keeping
  everything inside `< >` as it is.

### Change the menu

The menu is the `NAV` list near the top of `build.py`.

## Building on your own computer (optional)

```
pip install markdown
python3 build.py
cd docs && python3 -m http.server 8000   # then open http://localhost:8000
```

## Where things are

| Path | What it is |
|---|---|
| `src/pages/` | One file per page |
| `src/news/` | One file per news item |
| `src/settings.txt` | Contact details used across the site |
| `src/images/` | Photos |
| `src/style.css`, `src/theme-mix.css` | The look of the site |
| `build.py` | Turns `src/` into the website, plus the menu and old-address redirects |
| `docs/` | The generated website (don't edit) |
| `.github/workflows/build.yml` | Rebuilds the site on every change and every night |
| `AGENTS.md` | Detailed notes for AI assistants |
