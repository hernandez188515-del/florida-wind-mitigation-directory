#!/usr/bin/env python3
"""Idempotent SEO / internal-linking pass for the whole site.

Run from the site root after any page is added or changed:

    python3 scripts/seo.py

It (re)writes only the blocks between its own markers, so running it twice is a no-op:
  * <!-- seo:head --> ... <!-- /seo:head -->   canonical, Open Graph, Twitter card, JSON-LD
  * the <nav> inside the site header              shared navigation
  * <!-- seo:related --> ... <!-- /seo:related -->  related pages + featured-listing call-out
  * sitemap.xml                                   rebuilt from the pages on disk
It never touches page body content, listings, or license tables.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_BASE = "https://hernandez188515-del.github.io/florida-wind-mitigation-directory"
SITE_NAME = "Florida Insurance Inspections"
SKIP_DIRS = {"assets", "data", "scripts", "guides", "advertise", ".git"}
# Guides that get a slot in the top nav (all guides still appear in the related-pages block).
NAV_GUIDES = {
    "guides/wind-mitigation-vs-4-point-vs-roof-certification/": "Which inspection?",
    "guides/2026-wind-mitigation-form-question-by-question/": "The 2026 form",
    "guides/citizens-4-point-and-roof-age-requirements/": "Citizens rules",
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def text_of(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def git_lastmod(rel: str) -> str:
    from datetime import date
    dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        return date.today().isoformat()
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    from datetime import date
    return date.today().isoformat()


def discover():
    pages = []
    home = ROOT / "index.html"
    pages.append({"kind": "home", "rel": "index.html", "url": "", "depth": 0})
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith(".")):
        f = d / "index.html"
        if not f.exists():
            continue
        t = f.read_text()
        m = re.search(r"<h1>Wind mitigation and 4-point inspectors in ([^<]+)</h1>", t)
        if not m:
            continue
        name = html.unescape(m.group(1)).strip()
        cnt = re.search(r'<span class="pill">([\d,]+) inspectors in the main table</span>', t)
        companies = [text_of(h) for h in re.findall(r'<article class="listing">\s*<h3>(.*?)<span class="badge"', t, re.S)]
        pages.append({"kind": "county", "rel": f"{d.name}/index.html", "url": f"{d.name}/", "depth": 1,
                      "name": name, "count": int(cnt.group(1).replace(",", "")) if cnt else 0,
                      "companies": companies})
    for f in sorted((ROOT / "guides").glob("*/index.html")):
        t = f.read_text()
        h1 = re.search(r"<h1>(.*?)</h1>", t, re.S)
        pages.append({"kind": "guide", "rel": str(f.relative_to(ROOT)), "url": str(f.parent.relative_to(ROOT)) + "/",
                      "depth": 2, "name": text_of(h1.group(1)) if h1 else f.parent.name})
    adv = ROOT / "advertise" / "index.html"
    if adv.exists():
        pages.append({"kind": "advertise", "rel": "advertise/index.html", "url": "advertise/", "depth": 1,
                      "name": "Featured listings for licensed inspectors"})
    return pages


def ld(obj) -> str:
    return '  <script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>\n"


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


def faq_from(t: str):
    qa = re.findall(r'<div class="faq-item"[^>]*>\s*<h3[^>]*>(.*?)</h3>\s*(.*?)</div>', t, re.S)
    if not qa:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": text_of(q),
                            "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", text_of(a))}}
                           for q, a in qa]}


def head_block(page, t, pages):
    title = text_of(re.search(r"<title>(.*?)</title>", t, re.S).group(1))
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = html.unescape(desc_m.group(1)) if desc_m else title
    url = f"{SITE_BASE}/{page['url']}"
    home_url = f"{SITE_BASE}/"
    og_type = "article" if page["kind"] == "guide" else "website"
    out = ["  <!-- seo:head -->\n",
           f'  <link rel="canonical" href="{esc(url)}">\n',
           f'  <meta property="og:type" content="{og_type}">\n',
           f'  <meta property="og:site_name" content="{SITE_NAME}">\n',
           f'  <meta property="og:title" content="{esc(title)}">\n',
           f'  <meta property="og:description" content="{esc(desc)}">\n',
           f'  <meta property="og:url" content="{esc(url)}">\n',
           '  <meta property="og:locale" content="en_US">\n',
           '  <meta name="twitter:card" content="summary">\n',
           f'  <meta name="twitter:title" content="{esc(title)}">\n',
           f'  <meta name="twitter:description" content="{esc(desc)}">\n']
    if page["kind"] == "home":
        out.append(ld({"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME,
                       "url": home_url, "inLanguage": "en-US", "description": desc}))
        others = [p for p in pages if p["kind"] in ("county", "guide")]
        out.append(ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Directory pages and guides",
                       "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                            "name": (f"{p['name']} County inspectors" if p["kind"] == "county" else p["name"]),
                                            "url": f"{SITE_BASE}/{p['url']}"} for i, p in enumerate(others)]}))
    elif page["kind"] == "county":
        out.append(ld(breadcrumb([("Home", home_url), (f"{page['name']} County", url)])))
        if page["companies"]:
            out.append(ld({"@context": "https://schema.org", "@type": "ItemList",
                           "name": f"{page['name']} County companies whose websites advertise wind mitigation or 4-point inspections",
                           "numberOfItems": len(page["companies"]),
                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c}
                                               for i, c in enumerate(page["companies"])]}))
    elif page["kind"] == "guide":
        out.append(ld(breadcrumb([("Home", home_url), ("Guides", home_url + "#guides"), (page["name"], url)])))
        out.append(ld({"@context": "https://schema.org", "@type": "Article", "headline": page["name"],
                       "description": desc, "mainEntityOfPage": url, "dateModified": git_lastmod(page["rel"]),
                       "publisher": {"@type": "Organization", "name": SITE_NAME, "url": home_url}}))
        faq = faq_from(t)
        if faq:
            out.append(ld(faq))
    elif page["kind"] == "advertise":
        out.append(ld(breadcrumb([("Home", home_url), ("Featured listings", url)])))
    out.append("  <!-- /seo:head -->\n")
    return "".join(out)


def nav_block(page, pages):
    pre = "../" * page["depth"]
    links = [("Home", pre or "./", page["kind"] == "home"),
             ("County directories", f"{pre}#directories", False)]
    for g in pages:
        if g["kind"] == "guide" and g["url"] in NAV_GUIDES:
            links.append((NAV_GUIDES[g["url"]], pre + g["url"], page is g))
    links.append(("For inspectors", pre + "advertise/", page["kind"] == "advertise"))
    if page["kind"] == "county":
        links.append(("Full license list", "#full-list", False))
    items = "".join(
        f'\n        <a href="{esc(h)}"' + (' aria-current="page"' if cur else "") + f">{esc(n)}</a>"
        for n, h, cur in links)
    return f"<nav aria-label=\"Main\">{items}\n      </nav>"


def related_block(page, pages):
    pre = "../" * page["depth"]
    counties = [p for p in pages if p["kind"] == "county"]
    guides = [p for p in pages if p["kind"] == "guide"]
    lis = []
    for p in counties:
        if p is page:
            continue
        lis.append(f'<li><a href="{esc(pre + p["url"])}">{esc(p["name"])} County inspectors</a>'
                   + (f' <span class="muted">({p["count"]:,} licenses)</span>' if p["count"] else "") + "</li>")
    for g in guides:
        if g is page:
            continue
        lis.append(f'<li><a href="{esc(pre + g["url"])}">{esc(g["name"])}</a></li>')
    cta = ""
    if page["kind"] in ("county", "guide", "home"):
        where = f"in {esc(page['name'])} County" if page["kind"] == "county" else "in Florida"
        cta = (
            '\n        <div class="cta-box" id="featured-listing">'
            f'\n          <h2>Are you a licensed inspector {where}? Get a featured listing.</h2>'
            '\n          <p>Featured listings put your company, the inspections you offer, and your published prices at the top of the county page homeowners use to find wind mitigation, 4-point, and roof certification inspectors. We only feature companies whose license we can match to the official DBPR file. Founding rate: $29/month for the first 3 months, then $49/month or $399/year.</p>'
            f'\n          <p><a class="btn btn-primary" href="{esc(pre)}advertise/">How featured listings work</a></p>'
            '\n        </div>'
        )
    return (
        "<!-- seo:related -->\n"
        '  <section class="section related" aria-labelledby="related-h">\n'
        '    <div class="wrap">'
        f"{cta}\n"
        '        <h2 id="related-h">More Florida inspection pages</h2>\n'
        f'        <ul class="related-list">{"".join(lis)}</ul>\n'
        "    </div>\n"
        "  </section>\n"
        "  <!-- /seo:related -->\n"
    )


def process(page, pages):
    path = ROOT / page["rel"]
    t = path.read_text()
    orig = t
    t = re.sub(r"  <!-- seo:head -->.*?<!-- /seo:head -->\n", "", t, flags=re.S)
    if page["kind"] == "county" and page["count"]:
        nco = len(page["companies"])
        desc = (f"{page['count']:,} licensed home inspectors in {page['name']} County, FL, from official DBPR records"
                + (f", plus {nco} compan{'ies' if nco != 1 else 'y'} whose own sites advertise wind mitigation or 4-point inspections." if nco else
                   ", for wind mitigation, 4-point, and roof certification inspections."))
        t = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', t, count=1)
    t = t.replace("</head>", head_block(page, t, pages) + "</head>", 1)
    t = re.sub(r"<nav[^>]*>.*?</nav>", lambda m: nav_block(page, pages), t, count=1, flags=re.S)
    t = re.sub(r"\n  <!-- seo:related -->.*?<!-- /seo:related -->\n", "", t, flags=re.S)
    if True:
        t = t.replace("\n  <footer>", "\n  " + related_block(page, pages) + "\n  <footer>", 1)
    if t != orig:
        path.write_text(t)
        return True
    return False


def write_sitemap(pages):
    rows = []
    for p in pages:
        freq = "monthly" if p["kind"] in ("guide", "advertise") else "weekly"
        rows.append("  <url>\n"
                    f"    <loc>{SITE_BASE}/{p['url']}</loc>\n"
                    f"    <lastmod>{git_lastmod(p['rel'])}</lastmod>\n"
                    f"    <changefreq>{freq}</changefreq>\n"
                    "  </url>\n")
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "".join(rows) + "</urlset>\n")


def main():
    pages = discover()
    changed = [p["rel"] for p in pages if process(p, pages)]
    write_sitemap(pages)
    print(f"{len(pages)} pages; updated: {', '.join(changed) or 'none'}; sitemap rebuilt")


if __name__ == "__main__":
    main()
