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
        ("Baptism", "baptism.html", "baptism"),
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


def parse(path):
    text = path.read_text(encoding="utf-8")
    head, body = text.split("\n---\n", 1)
    meta = {}
    for line in head.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
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


def page(meta, body):
    title = meta["title"]
    full_title = SITE_NAME if meta.get("nav") == "home" else f"{title} | {SITE_NAME}"
    desc = meta.get("description", "Church of England parishes of Burwash, Burwash Weald and Etchingham, East Sussex.")
    c = CONTACT
    theme_css = f'\n<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@200..500&display=swap" rel="stylesheet">\n<link rel="stylesheet" href="theme-{THEME}.css">' if THEME else ""
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
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Indie+Flower&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">{theme_css}
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
          '<a class="btn wa-btn" href="https://chat.whatsapp.com/Hnf8zILV8Rk8XnDT7AK2zu">Join on WhatsApp</a></div>')


def load_news():
    posts = []
    for f in sorted((SRC / "news").glob("*.html")):
        meta, body = parse(f)
        meta["slug"] = "news-" + f.stem + ".html"
        meta["body"] = body
        posts.append(meta)
    posts.sort(key=lambda m: (m["date"], m["slug"]), reverse=True)
    return posts


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
            f'<p class="place">{nice_date(m["date"])}</p><h3>{html.escape(m["title"])}</h3>'
            f'<p>{html.escape(m["summary"])}</p><span class="read">Read more &rarr;</span></div></a>')


def build(with_redirects=True, out=None):
    global OUT
    if out: OUT = out
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    posts = load_news() if (SRC / "news").exists() else []
    current = [m for m in posts if is_current(m)]
    latest = "".join(news_card(m) for m in current[:6])
    for p in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(p)
        body = body.replace("<!--LATEST_NEWS-->", latest).replace("<!--NEWS_BAR-->", news_bar(posts)).replace("<!--WA_BOX-->", WA_BOX)
        (OUT / p.name).write_text(page(meta, body), encoding="utf-8")
    listing = "".join(news_card(m) for m in current) or "<p>No news at the moment.</p>"
    news_body = ('<div class="page-head"><div class="wrap"><h1>News</h1><p>What\'s happening across our three churches.</p></div></div>'
                 f'<section class="block"><div class="wrap">{WA_BOX}<div class="grid-3">{listing}</div></div></section>')
    (OUT / "news.html").write_text(page({"title": "News", "nav": "news", "description": "News from the benefice of Burwash, Burwash Weald and Etchingham."}, news_body), encoding="utf-8")
    for m in posts:
        img = f'<div class="photo wide"><img src="{m["image"]}" alt=""></div>' if m.get("image") else ""
        body = (f'<div class="page-head"><div class="wrap"><p class="eyebrow">{nice_date(m["date"])}</p><h1>{html.escape(m["title"])}</h1></div></div>'
                f'<section class="block"><div class="wrap narrow prose">{img}{m["body"]}<p style="margin-top:2rem"><a href="news.html">&larr; All news</a></p></div></section>')
        (OUT / m["slug"]).write_text(page({"title": m["title"], "nav": "news", "description": m["summary"]}, body), encoding="utf-8")
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
