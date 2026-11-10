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
    ("Our churches", "index.html#churches", "churches", [
        ("St Bartholomew's, Burwash", "burwash.html", "burwash"),
        ("St Philip's, Burwash Weald", "burwash-weald.html", "burwash-weald"),
        ("Etchingham", "etchingham.html", "etchingham"),
    ]),
    ("Get involved", "choir.html", "activities", [
        ("Choir", "choir.html", "choir"),
        ("Bellringing", "bellringing.html", "bellringing"),
    ]),
    ("Safeguarding", "safeguarding.html", "safeguarding", []),
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

WORDMARK = '<span class="wm"><b>B</b>urwash<span class="sep">,</span> <b>B</b>urwash <b>W</b>eald<span class="sep">,</span> <b>E</b>tchingham</span>'
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
      <p><a href="{c['facebook']}">Follow us on Facebook</a></p>
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


def build(with_redirects=True, out=None):
    global OUT
    if out: OUT = out
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for p in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(p)
        (OUT / p.name).write_text(page(meta, body), encoding="utf-8")
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
        # CNAME is added only once DNS is switched over (see README)
        (OUT / ".nojekyll").write_text("")
    print("Built", len(list(OUT.glob("*.html"))), "pages into", OUT)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:  # python3 build.py <theme> <outdir>
        THEME = sys.argv[1]
        build(with_redirects=False, out=pathlib.Path(sys.argv[2]))
    else:
        build()
