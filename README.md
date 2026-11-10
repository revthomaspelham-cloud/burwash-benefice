# Burwash Benefice website

Source for https://burwashbenefice.org.uk

- `src/pages/` – one file per page (title/nav/description header, then HTML)
- `src/style.css` – the site's styles
- `src/images/` – photos
- `build.py` – run `python3 build.py` to regenerate `docs/`, which GitHub Pages serves

Old website-builder addresses (e.g. `/Weddings/`) redirect to the new pages.

When switching the domain over: add `docs/CNAME` containing `burwashbenefice.org.uk`
(via build.py), set the custom domain in Settings → Pages, and point the DNS at GitHub Pages.
