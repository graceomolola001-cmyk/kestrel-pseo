#!/usr/bin/env python3
"""
Static page generator for the Kestrel eCampus demo.

Usage:
    python build.py                      build into dist/ (pages marked noindex)
    python build.py --index              allow indexing and write sitemap.xml
    python build.py --faq-schema         also write FAQPage JSON-LD
    python build.py --base-url https://your-site.example   set canonical URLs

Rules:
  * Runs the checker first. If any FIX exists, nothing is built.
  * Only rows with status=publish are built.
  * Standard library only.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import urlparse

import pseo_checker as pc

SITE = "Kestrel eCampus"
PREFIX = ""  # set from --base-url: "" for a root site, "/repo-name" for a GitHub project site
CSS = """
:root{--ink:#1d2433;--soft:#566074;--line:#d6dbe5;--bg:#f6f7f9;--card:#fff;--accent:#1f4fa3;--warn:#fff1c2}
*{box-sizing:border-box}
body{margin:0;font:17px/1.65 Georgia,'Times New Roman',serif;color:var(--ink);background:var(--bg)}
.banner{background:var(--warn);font:14px/1.4 system-ui,sans-serif;padding:8px 16px;text-align:center}
header.site{font:600 18px system-ui,sans-serif;padding:14px 20px;background:var(--card);border-bottom:1px solid var(--line)}
header.site a{color:var(--ink);text-decoration:none}
main{max-width:760px;margin:0 auto;padding:20px}
nav.crumbs{font:14px system-ui,sans-serif;color:var(--soft)}
nav.crumbs a{color:var(--accent)}
h1{font:700 34px/1.15 system-ui,sans-serif;margin:12px 0}
h2{font:600 21px system-ui,sans-serif;margin:28px 0 8px}
h3{font:600 17px system-ui,sans-serif;margin:16px 0 2px}
dl.facts{display:grid;grid-template-columns:max-content 1fr;gap:6px 20px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;font-family:system-ui,sans-serif;font-size:16px}
dl.facts dt{color:var(--soft)} dl.facts dd{margin:0;font-weight:600}
.meta{font:13px system-ui,sans-serif;color:var(--soft);margin:6px 0 0}
a.cta{display:inline-block;margin:18px 0;background:var(--accent);color:#fff;font:600 16px system-ui,sans-serif;padding:12px 22px;border-radius:8px;text-decoration:none}
ul.links{padding-left:20px}
footer{font:13px system-ui,sans-serif;color:var(--soft);text-align:center;padding:30px 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}
.grid div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;font-family:system-ui,sans-serif;font-size:15px}
.grid b{display:block;margin-bottom:4px}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
"""
BANNER = ("Demo site for a programmatic SEO exercise. Kestrel eCampus is fictional, "
          "and every fee, date and requirement is made up.")


def esc(s):
    return html.escape(s, quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def path_for(r):
    return f"/programmes/online-{slugify(r['programme'])}-{slugify(r['country'])}/"


def name_for(r):
    return f"Online {r['programme']} in {r['country']}"


def meta_description(r):
    d = (f"{name_for(r)}: {r['fees']}, {r['duration']}, next intake {r['intake']}. "
         f"Entry: {r['entry']}.")
    if len(d) > 158:
        d = d[:157].rsplit(" ", 1)[0].rstrip(",.;:") + "..."
    return d


def faq(r):
    p, c = r["programme"], r["country"]
    return [
        (f"How much does the {p} programme cost in {c}?", f"The fee is {r['fees']}."),
        (f"What are the entry requirements for the {p} programme in {c}?", f"{r['entry']}."),
        (f"How long does the {p} programme take in {c}?", f"It takes {r['duration']}."),
        (f"When can I start the {p} programme in {c}?", f"The next intake is {r['intake']}."),
    ]


def head(title, desc, canonical, noindex):
    robots = "noindex, nofollow" if noindex else "index, follow"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(canonical)}">
<style>{CSS}</style>
</head>
<body>
<div class="banner">{esc(BANNER)}</div>
<header class="site"><a href="{PREFIX}/">{esc(SITE)}</a></header>
<main>
"""


FOOT = """
</main>
<footer>Kestrel eCampus is a fictional university used for a programmatic SEO practice project.</footer>
</body>
</html>
"""


def related(r, pub):
    same_prog = [x for x in pub if x["programme"] == r["programme"] and x is not r]
    same_country = [x for x in pub if x["country"] == r["country"] and x is not r]
    a = "".join(f'<li><a href="{PREFIX}{path_for(x)}">{esc(name_for(x))}</a></li>' for x in same_prog)
    b = "".join(f'<li><a href="{PREFIX}{path_for(x)}">{esc(name_for(x))}</a></li>' for x in same_country)
    out = ""
    if a:
        out += f"<h3>{esc(r['programme'])} in other countries</h3><ul class=\"links\">{a}</ul>"
    if b:
        out += f"<h3>Other programmes in {esc(r['country'])}</h3><ul class=\"links\">{b}</ul>"
    return out


def page(r, pub, base, noindex, faq_schema):
    n = name_for(r)
    title = f"{n}: fees, entry requirements and duration | {SITE}"
    canonical = base.rstrip("/") + path_for(r)
    qa = faq(r)
    qa_html = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in qa)
    ld = ""
    if faq_schema:
        data = {"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q,
                                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
        ld = f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="{PREFIX}/">Home</a> / <a href="{PREFIX}/programmes/">Programmes</a> / {esc(n)}</nav>
<h1>{esc(n)}</h1>
<p>Study the {esc(r['programme'])} fully online from {esc(r['country'])}.</p>
<h2>Key facts</h2>
<dl class="facts">
<dt>Fees</dt><dd data-field="fees">{esc(r['fees'])}</dd>
<dt>Duration</dt><dd data-field="duration">{esc(r['duration'])}</dd>
<dt>Next intake</dt><dd data-field="intake">{esc(r['intake'])}</dd>
<dt>Entry requirements</dt><dd data-field="entry">{esc(r['entry'])}</dd>
</dl>
<p class="meta">Source: {esc(r['source'])}. Last verified {esc(r['last_verified'])}.</p>
<h2>Who this suits</h2>
<p data-field="suits">{esc(r['suits'])}</p>
<h2>Questions</h2>
{qa_html}
<h2>Student support</h2>
<p>Every student gets a named adviser, an online library and a weekly live help session.</p>
<a class="cta" href="https://example.com/apply">Apply now</a>
<h2>Related programmes</h2>
{related(r, pub)}
{ld}"""
    return head(title, meta_description(r), canonical, noindex) + body + FOOT


def hub(pub, base, noindex, home=False):
    progs = []
    for r in pub:
        if r["programme"] not in progs:
            progs.append(r["programme"])
    cells = ""
    for p in progs:
        links = "".join(f'<a href="{PREFIX}{path_for(x)}">{esc(x["country"])}</a><br>'
                        for x in pub if x["programme"] == p)
        cells += f"<div><b>{esc(p)}</b>{links}</div>"
    if home:
        title = f"{SITE}: study online from Zambia, Ghana, Uganda and Nigeria"
        desc = f"{SITE} offers online degrees and diplomas to students in Zambia, Ghana, Uganda and Nigeria."
        h1 = f"Study online with {SITE}"
        canonical = base.rstrip("/") + "/"
    else:
        title = f"Online programmes by country | {SITE}"
        desc = f"Every online programme at {SITE}, with fees, entry requirements and intake dates for each country."
        h1 = "Online programmes"
        canonical = base.rstrip("/") + "/programmes/"
    body = f"""<h1>{esc(h1)}</h1>
<p>Choose a programme, then your country, to see fees, entry requirements, duration and the next intake.</p>
<div class="grid">{cells}</div>
"""
    return head(title, desc, canonical, noindex) + body + FOOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/pages.csv")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--base-url", default="https://example.com")
    ap.add_argument("--index", action="store_true", help="allow indexing and write sitemap.xml")
    ap.add_argument("--faq-schema", action="store_true", help="write FAQPage JSON-LD")
    a = ap.parse_args()
    global PREFIX
    PREFIX = urlparse(a.base_url).path.rstrip("/")

    rows, missing = pc.load(a.csv)
    if missing:
        print("Build stopped. Missing columns: " + ", ".join(missing))
        return 1
    findings = pc.check(rows)
    fixes = [f for f in findings if f[0] == "FIX"]
    reviews = [f for f in findings if f[0] == "REVIEW"]
    if fixes:
        print("Build stopped. Resolve these FIX items first:")
        for _, where, msg in fixes:
            print(f"  FIX  {where}: {msg}")
        print("Run: python pseo_checker.py " + a.csv)
        return 1

    pub = [r for r in rows if pc.status_of(r) == "publish"]
    held = [r for r in rows if pc.status_of(r) == "hold"]
    noindex = not a.index

    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    os.makedirs(os.path.join(a.out, "programmes"))

    def write(rel, text):
        p = os.path.join(a.out, *rel.strip("/").split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    for r in pub:
        write(path_for(r) + "index.html", page(r, pub, a.base_url, noindex, a.faq_schema))
    write("/programmes/index.html", hub(pub, a.base_url, noindex))
    write("/index.html", hub(pub, a.base_url, noindex, home=True))
    # In demo mode, Disallow keeps crawlers out entirely. (A crawler that is
    # blocked can never read a noindex tag, so on a real site you would not
    # combine the two.)
    robots = "User-agent: *\nDisallow: /\n" if noindex else (
        "User-agent: *\nAllow: /\n" + f"Sitemap: {a.base_url.rstrip('/')}/sitemap.xml\n")
    write("/robots.txt", robots)
    if not noindex:
        urls = "".join(
            f"<url><loc>{esc(a.base_url.rstrip('/') + path_for(r))}</loc>"
            f"<lastmod>{esc(r['last_verified'])}</lastmod></url>" for r in pub)
        write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>\n")

    print(f"Built {len(pub)} pages into {a.out}/  ({len(held)} held back)")
    print("Mode: " + ("INDEXABLE with sitemap.xml" if not noindex else "noindex (safe for a demo)"))
    if reviews:
        print(f"{len(reviews)} REVIEW items remain. Confirm each against its source:")
        for _, where, msg in reviews:
            print(f"  REVIEW {where}: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
