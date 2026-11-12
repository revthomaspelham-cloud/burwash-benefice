#!/usr/bin/env python3
"""Build the benefice website.

Each file in src/pages/ is a page fragment:

    title: Page title
    nav: key-of-active-nav-item
    description: one line for search engines
    ---
    <html body content>

Run `python3 build.py` and the finished site is written to docs/,
which GitHub Pages serves.
"""
import html
import re
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

SITE_NAME = "The Benefice of Burwash, Burwash Weald & Etchingham"
DOMAIN = "burwashbenefice.org.uk"

# (label, href, key, children)
NAV = [
    ("Home", "index.html", "home", []),
    ("Services", "services.html", "services", [
        ("Service calendar", "services.html", "services"),
        ("Baptism & confirmation", "baptism.html", "baptism"),
        ("Weddings", "weddings.html", "weddings"),
        ("Funerals", "funerals.html", "funerals"),
    ]),
    ("About us", "about.html", "about", [
        ("Who we are", "about.html", "about"),
        ("St Bartholomew's, Burwash", "burwash.html", "burwash"),
        ("St Philip's, Burwash Weald", "burwash-weald.html", "burwash-weald"),
        ("Etchingham", "etchingham.html", "etchingham"),
    ]),
    ("Get involved", "get-involved.html", "activities", [
        ("All the ways to get involved", "get-involved.html", "activities"),
        ("Choir", "choir.html", "choir"),
        ("Bellringing", "bellringing.html", "bellringing"),
        ("Sidespeople & welcome", "get-involved.html#sidespeople", "sidespeople"),
        ("Readers", "get-involved.html#readers", "readers"),
        ("3Cs: Coffee, Cake & Chat", "get-involved.html#3cs", "3cs"),
        ("Pastoral visiting", "get-involved.html#pastoral", "pastoral"),
        ("House groups", "get-involved.html#house-groups", "house-groups"),
        ("Toddler groups", "get-involved.html#toddlers", "toddlers"),
    ]),
    ("News", "news.html", "news", []),
    ("Safeguarding", "safeguarding.html", "safeguarding", []),
    ("Contact", "contact.html", "contact", []),
    ("Give", "give.html", "give", []),
]

# Old website-builder URLs -> new pages (kept working via redirect stubs)
REDIRECTS = {
    "Safeguarding": "safeguarding.html",
    "Services": "services.html",
    "Weddings": "weddings.html",
    "Funerals": "funerals.html",
    "Baptism": "baptism.html",
    "St-Bartholomews": "burwash.html",
    "Burwash-Weald": "burwash-weald.html",
    "Etchingham": "etchingham.html",
    "Bellringing": "bellringing.html",
    "Choir": "choir.html",
}

CONTACT = {
    "phone": "07856 256 174",
    "phone_href": "+447856256174",
    "email": "revthomaspelham@gmail.com",
    "facebook": "https://www.facebook.com/profile.php?id=100087591101156",
    "whatsapp": "https://chat.whatsapp.com/Hnf8zILV8Rk8XnDT7AK2zu",
}


def last_sunday(year, month):
    d = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    return d - datetime.timedelta(days=(d.weekday() + 1) % 7)


def is_bst(day):
    """British Summer Time runs from the last Sunday in March to the last Sunday in October."""
    return last_sunday(day.year, 3) <= day < last_sunday(day.year, 10)


def load_settings():
    """src/settings.txt: 'key: value' lines. Use {{key}} anywhere in page or news text.
    A line 'key from YYYY-MM-DD: value' takes over from that date (the site rebuilds daily)."""
    f = SRC / "settings.txt"
    out, dated = {}, []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and ":" in line:
                k, v = line.split(":", 1)
                m = re.fullmatch(r"(\S+)\s+from\s+(\d{4}-\d{2}-\d{2})", k.strip())
                if m:
                    dated.append((m.group(2), m.group(1), v.strip()))
                else:
                    out[k.strip()] = v.strip()
    today = datetime.date.today().isoformat()
    # Automatic: evening service time follows British Summer Time
    out.setdefault("season", season_class())
    out.setdefault("evening_time", "6pm" if is_bst(datetime.date.today()) else "4.30pm")
    for d, k, v in sorted(dated):
        if d <= today:
            out[k] = v
    return out


SETTINGS = None


def fill(text):
    global SETTINGS
    if SETTINGS is None:
        SETTINGS = load_settings()
    for k, v in SETTINGS.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def md(text):
    """Markdown (with raw HTML allowed) -> HTML."""
    import markdown
    return markdown.markdown(text, extensions=["extra", "sane_lists"], output_format="html5")


def parse(path):
    """Front-matter ('key: value' lines), a line '---', then the body.
    .md files: body is Markdown. .html files: body is HTML."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    head, body = text.split("\n---\n", 1)
    meta = {}
    for line in head.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = fill(v.strip())
    body = fill(body)
    if path.suffix == ".md":
        body = md(body)
        if meta.get("layout", "prose") == "prose" and path.parent.name in ("pages", "drafts"):
            intro = f'<p>{meta["intro"]}</p>' if meta.get("intro") else ""
            body = (f'<div class="page-head"><div class="wrap"><h1>{meta.get("heading", meta["title"])}</h1>{intro}</div></div>'
                    f'<section class="block"><div class="wrap narrow prose">{body}</div></section>')
    return meta, body


def child_keys(children):
    return {c[2] for c in children}


def render_nav(active):
    items = []
    for label, href, key, children in NAV:
        is_active = active == key or active in child_keys(children)
        cls = ' class="active"' if is_active else ""
        if children:
            sub = "".join(
                f'<li><a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{html.escape(l)}</a></li>'
                for l, h, k in children
            )
            items.append(
                f'<li class="has-sub"{cls[0:0]}><a href="{href}"{cls}>{html.escape(label)}</a>'
                f'<ul class="sub">{sub}</ul></li>'
            )
        else:
            cur = ' aria-current="page"' if is_active else ""
            extra = ' class="nav-give"' if key == "give" else ""
            items.append(f'<li{extra}><a href="{href}"{cls}{cur}>{html.escape(label)}</a></li>')
    return "".join(items)


LOGO_SVG = """<svg class="logo-mark" viewBox="0 0 40 48" aria-hidden="true"><path d="M20 2v8M16 6h8M12 18l8-8 8 8v28H12z M6 46V28l6-5M34 46V28l-6-5M4 46h32" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M17 46v-9a3 3 0 0 1 6 0v9" fill="none" stroke="currentColor" stroke-width="2"/></svg>"""


THEME = "mix"  # live design. Alternatives kept for reference: None (original plum), "blend", "full"

WORDMARK = '<span class="wm"><span class="nm"><b>B</b>urwash<span class="sep">,</span></span> <span class="nm"><b>B</b>urwash <b>W</b>eald<span class="sep">,</span></span> <span class="nm"><b>E</b>tchingham</span></span>'
TAGLINE = '<span class="tagline">Worship for Everybody</span>'


def _page(meta, body):
    title = meta["title"]
    full_title = SITE_NAME if meta.get("nav") == "home" else f"{title} | {SITE_NAME}"
    desc = meta.get("description", "Church of England parishes of Burwash, Burwash Weald and Etchingham, East Sussex.")
    c = CONTACT
    theme_css = f'\n<link rel="stylesheet" href="theme-{THEME}.css">' if THEME else ""
    fonts = "family=Cormorant+Garamond:wght@500;600;700&family=Indie+Flower&family=Source+Sans+3:wght@400;600"
    fonts += {"mix": "&family=Oswald:wght@200..500", "full": "&family=Bebas+Neue", "blend": "&family=Bebas+Neue"}.get(THEME, "")
    if THEME in ("full", "mix"):
        brand_text = f'<span>{WORDMARK}{TAGLINE}</span>'
    elif THEME == "blend":
        brand_text = f'<span><span class="brand-small">The Benefice of</span><span class="brand-big">Burwash, Burwash Weald &amp; Etchingham</span>{TAGLINE}</span>'
    else:
        brand_text = '<span><span class="brand-small">The Benefice of</span><span class="brand-big">Burwash, Burwash Weald &amp; Etchingham</span></span>'
    wm = meta.get("wordmark")
    if THEME and wm:
        body = body.replace('<div class="page-head"><div class="wrap">', f'<div class="page-head has-wm"><div class="wrap"><p class="church-wm">{wm}</p>{TAGLINE}', 1)
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">{theme_css}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(SITE_NAME)}">
<meta property="og:title" content="{html.escape(title if meta.get("nav") != "home" else SITE_NAME)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="https://{DOMAIN}/{meta.get("url", "")}">
<meta property="og:image" content="https://{DOMAIN}/{meta.get("share_image") or meta.get("image") or "images/weald-view.jpg"}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="images/favicon.png">
<link rel="apple-touch-icon" href="images/apple-touch-icon.png">
</head>
<body class="{('theme-' + THEME) if THEME else ''}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html"><img class="logo-mark" src="images/crossburst.png" alt="" width="40" height="50">{brand_text}</a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav id="site-nav" class="site-nav" aria-label="Main"><ul>{render_nav(meta.get("nav", ""))}</ul></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <h2>Get in touch</h2>
      <p>The Rector, Revd Thomas Pelham</p>
      <p><a href="tel:{c['phone_href']}">{c['phone']}</a><br>
      <a href="mailto:{c['email']}">{c['email']}</a></p>
      <p><a href="contact.html">Send us a message</a> &middot; <a href="{c['facebook']}">Facebook</a> &middot; <a href="{c['whatsapp']}">WhatsApp</a></p>
    </div>
    <div>
      <h2>Our churches</h2>
      <ul class="plain">
        <li><a href="burwash.html">St Bartholomew's, Burwash</a></li>
        <li><a href="burwash-weald.html">St Philip's, Burwash Weald</a></li>
        <li><a href="etchingham.html">The Assumption of the Blessed Virgin &amp; St Nicholas, Etchingham</a></li>
      </ul>
    </div>
    <div>
      <h2>Support us</h2>
      <p>Give regularly through the Parish Giving Scheme:</p>
      <ul class="plain">
        <li><a href="https://www.parishgiving.org.uk/donors/find-your-parish/burwash-st-bartholomews-etchingham">St Bartholomew's, Burwash</a></li>
        <li><a href="https://www.parishgiving.org.uk/donors/find-your-parish/burwash-weald-st-philip-burwash-common">St Philip's, Burwash Weald</a></li>
        <li><a href="https://www.parishgiving.org.uk/donors/find-your-parish/etchingham-st-mary-w-nicholas-hastings-tunbridge-wells">Etchingham</a></li>
      </ul>
    </div>
    <div>
      <h2>Safeguarding</h2>
      <p>If you are worried about a child or adult, see our <a href="safeguarding.html">safeguarding page</a> for who to contact.</p>
      <a class="cofe" href="https://www.churchofengland.org/"><img src="images/cofe-white.png" alt="The Church of England" width="90"></a>
      <p class="small">Part of the Church of England, in the <a href="https://www.chichester.anglican.org/">Diocese of Chichester</a>.</p>
      <p class="small">Each parish is run by its Parochial Church Council. St Bartholomew's PCC is a registered charity (no. 1133028); the PCCs of St Philip's and Etchingham are excepted charities.</p>
    </div>
  </div>
</footer>
<script>
(function(){{var b=document.querySelector('.menu-toggle'),n=document.getElementById('site-nav');
b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o);}});}})();
// Hide news whose 'until' date has passed (shown until the end of that day)
(function(){{var t=new Date();t.setHours(0,0,0,0);
document.querySelectorAll('[data-until]').forEach(function(el){{var d=new Date(el.dataset.until+'T00:00:00');if(d<t)el.remove();}});
var bar=document.querySelector('.news-bar');if(!bar)return;var it=bar.querySelectorAll('.nb-item');
if(!it.length){{bar.remove();return;}}var i=0,paused=false;it[0].classList.add('on');if(it.length<2)return;
bar.addEventListener('mouseenter',function(){{paused=true;}});bar.addEventListener('mouseleave',function(){{paused=false;}});
bar.addEventListener('focusin',function(){{paused=true;}});bar.addEventListener('focusout',function(){{paused=false;}});
setInterval(function(){{if(paused)return;it[i].classList.remove('on');i=(i+1)%it.length;it[i].classList.add('on');}},6000);}})();
</script>
</body>
</html>
"""


def redirect_stub(target):
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=../{target}">
<link rel="canonical" href="https://{DOMAIN}/{target}">
<title>Moved</title></head>
<body><p>This page has moved to <a href="../{target}">{target}</a>.</p></body></html>
"""


import datetime


WA_BOX = ('<div class="wa-box"><div><h3>Weekly news on WhatsApp</h3><p>Join our WhatsApp community to get each week\'s services and events straight to your phone.</p></div>'
          '<a class="btn wa-btn" href="{{whatsapp_link}}">Join on WhatsApp</a></div>')


def load_news():
    posts = []
    for f in sorted(list((SRC / "news").glob("*.html")) + list((SRC / "news").glob("*.md"))):
        if f.name.startswith("_"):
            continue  # _template.md etc.
        meta, body = parse(f)
        meta["slug"] = "news-" + f.stem + ".html"
        meta["body"] = body
        posts.append(meta)
    clocks = clocks_post()
    if clocks:
        posts.append(clocks)
    posts.sort(key=lambda m: (m["date"], m["slug"]), reverse=True)
    return posts


def clocks_post(today=None, days_before=21):
    """Automatic reminder, built from src/news/_clocks.md, shown for three weeks before
    each change of the clocks (last Sunday of March and of October)."""
    tpl = SRC / "news" / "_clocks.md"
    today = today or datetime.date.today()
    if not tpl.exists():
        return None
    changes = sorted(last_sunday(y, m) for y in (today.year, today.year + 1) for m in (3, 10))
    change = next(d for d in changes if d >= today)
    start = change - datetime.timedelta(days=days_before)
    if today < start:
        return None
    forward = change.month == 3
    fields = {
        "clocks_way": "forward" if forward else "back",
        "clocks_day": f"Sunday {change.day} {change.strftime('%B')}",
        "clocks_new_time": "6pm" if forward else "4.30pm",
        "clocks_old_time": "4.30pm" if forward else "6pm",
    }
    text = tpl.read_text(encoding="utf-8")
    text = text.split("\n(This reminder appears")[0]
    for k, v in fields.items():
        text = text.replace("{{" + k + "}}", v)
    tmp = OUT.parent / ".clocks-tmp.md"
    head, body = text.split("\n---\n", 1)
    head += f"\ndate: {start.isoformat()}\nuntil: {change.isoformat()}"
    tmp.write_text(head + "\n---\n" + body, encoding="utf-8")
    try:
        meta, body = parse(tmp)
    finally:
        tmp.unlink()
    meta["slug"] = f"news-clocks-{change.isoformat()}.html"
    meta["body"] = body
    return meta


def nice_date(d):
    dt = datetime.date.fromisoformat(d)
    return f"{dt.day} {dt.strftime('%B %Y')}"


def is_current(m):
    """A post is current until the end of its 'until' date (no date = always current)."""
    return not m.get("until") or datetime.date.fromisoformat(m["until"]) >= datetime.date.today()


def until_attr(m):
    return f' data-until="{m["until"]}"' if m.get("until") else ""


def news_bar(posts):
    items = [m for m in posts if is_current(m) and m.get("headline")]
    items.sort(key=lambda m: m.get("until") or "9999")
    if not items:
        return ""
    lis = "".join(f'<p class="nb-item"{until_attr(m)}>{m["headline"]} <a href="{m["slug"]}">Find out more</a></p>' for m in items)
    return f'<div class="notice news-bar" aria-live="polite"><div class="wrap"><div class="nb-items">{lis}</div></div></div>'


def news_card(m):
    img = f'<div class="photo"><img src="{m["image"]}" alt="" loading="lazy"></div>' if m.get("image") else ""
    return (f'<a class="card news-card"{until_attr(m)} href="{m["slug"]}">{img}<div class="body">'
            f'<h3>{html.escape(m["title"])}</h3>'
            f'<p>{html.escape(m["summary"])}</p><span class="read">Read more &rarr;</span></div></a>')


def season_class(day=None):
    """Same rules as the script on the home page, decided at build time (the site
    rebuilds daily) so only one banner photo is downloaded."""
    day = day or datetime.date.today()
    advent = datetime.date(day.year, 11, 27)
    while advent.weekday() != 6:
        advent += datetime.timedelta(days=1)
    if (day.month == 1 and day.day <= 6) or day >= advent:
        return "season-winter"
    if day.month in (3, 4):
        return "season-spring"
    if 5 <= day.month <= 9:
        return "season-summer"
    return ""


def page(meta, body):
    return fill(_page(meta, body))


def build(with_redirects=True, out=None):
    global OUT
    if out: OUT = out
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    st = load_settings()
    CONTACT.update({k: v for k, v in {
        "phone": st.get("rector_phone"), "phone_href": st.get("rector_phone_link", "").replace("tel:", ""),
        "email": st.get("rector_email"), "facebook": st.get("facebook_link"), "whatsapp": st.get("whatsapp_link"),
    }.items() if v})
    posts = load_news() if (SRC / "news").exists() else []
    current = [m for m in posts if is_current(m)]
    latest = "".join(news_card(m) for m in current[:3])
    for p in sorted(list((SRC / "pages").glob("*.html")) + list((SRC / "pages").glob("*.md"))):
        meta, body = parse(p)
        meta["url"] = "" if p.stem == "index" else p.stem + ".html"
        body = body.replace("<!--LATEST_NEWS-->", latest).replace("<!--NEWS_BAR-->", news_bar(posts)).replace("<!--WA_BOX-->", WA_BOX)
        (OUT / (p.stem + ".html")).write_text(page(meta, body), encoding="utf-8")
    listing = "".join(news_card(m) for m in current) or "<p>No news at the moment.</p>"
    news_body = ('<div class="page-head"><div class="wrap"><h1>News</h1><p>What\'s happening across our three churches.</p></div></div>'
                 f'<section class="block"><div class="wrap">{WA_BOX}<div class="grid-3">{listing}</div></div></section>')
    (OUT / "news.html").write_text(page({"title": "News", "nav": "news", "url": "news.html", "description": "News from the benefice of Burwash, Burwash Weald and Etchingham."}, news_body), encoding="utf-8")
    for m in posts:
        img = f'<div class="photo wide"><img src="{m["image"]}" alt=""></div>' if m.get("image") else ""
        body = (f'<div class="page-head"><div class="wrap"><p class="eyebrow">News</p><h1>{html.escape(m["title"])}</h1><p>Posted: {nice_date(m["date"])}</p></div></div>'
                f'<section class="block"><div class="wrap narrow prose">{img}{m["body"]}<p style="margin-top:2rem"><a href="news.html">&larr; All news</a></p></div></section>')
        (OUT / m["slug"]).write_text(page({"title": m["title"], "nav": "news", "description": m["summary"], "url": m["slug"], "image": m.get("image", "")}, body), encoding="utf-8")
    nf = ('<div class="page-head"><div class="wrap"><h1>Page not found</h1><p>Sorry, we can\'t find that page.</p></div></div>'
          '<section class="block"><div class="wrap narrow prose"><p>It may have moved when we updated our website. Try our '
          '<a href="index.html">home page</a>, <a href="services.html">service times</a> or <a href="contact.html">contact us</a>.</p></div></section>')
    (OUT / "404.html").write_text(page({"title": "Page not found", "url": "404.html"}, nf).replace("<head>", '<head>\n<base href="/">', 1), encoding="utf-8")
    shutil.copy(SRC / "style.css", OUT / "style.css")
    if THEME:
        shutil.copy(SRC / f"theme-{THEME}.css", OUT / f"theme-{THEME}.css")
    if (SRC / "images").exists():
        shutil.copytree(SRC / "images", OUT / "images")
    if with_redirects:
        for old, new in REDIRECTS.items():
            d = OUT / old
            d.mkdir()
            (d / "index.html").write_text(redirect_stub(new), encoding="utf-8")
        (OUT / "CNAME").write_text(DOMAIN + "\n")
        (OUT / ".nojekyll").write_text("")
    print("Built", len(list(OUT.glob("*.html"))), "pages into", OUT)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:  # python3 build.py <theme> <outdir>
        THEME = sys.argv[1]
        build(with_redirects=False, out=pathlib.Path(sys.argv[2]))
    else:
        build()
