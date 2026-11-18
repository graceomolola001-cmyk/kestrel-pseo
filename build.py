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
:root{--ink:#18233a;--muted:#607087;--accent:#533e80;--teal:#166d73;--line:#dfe3ec;--bg:#f6f8fb;--card:#fff}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--bg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--accent);text-underline-offset:3px}:focus-visible{outline:3px solid #e9ac4e;outline-offset:3px}
.skip-link{position:absolute;top:-100px;left:1rem;background:white;padding:10px;z-index:20}.skip-link:focus{top:1rem}.banner{background:#172339;color:#f2f4f8;text-align:center;font-size:.77rem;padding:8px 16px}
header.site{background:#fff;border-bottom:1px solid var(--line)}.nav-wrap{max-width:1190px;margin:auto;display:flex;justify-content:space-between;align-items:center;padding:16px 28px;gap:12px}.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:800;letter-spacing:-.04em}.brand-mark{background:linear-gradient(135deg,#533e80,#166d73);border-radius:11px;color:#fff;width:40px;height:40px;display:grid;place-items:center;font-size:1.3rem}.site-nav{display:flex;align-items:center;gap:18px;font-size:.86rem;font-weight:700}.site-nav a{text-decoration:none}.nav-cta{border:1px solid var(--line);border-radius:10px;padding:10px 13px}
main{max-width:1190px;margin:auto;padding:32px 28px 70px;min-height:65vh}.hero{background:linear-gradient(115deg,#f1ecfa,#e6f4f2);border-radius:28px;border:1px solid #e2dceb;padding:clamp(27px,6vw,66px);box-shadow:0 16px 44px #26204d0a}.eyebrow,.card-flag{font-size:.73rem;letter-spacing:.11em;font-weight:850;color:var(--teal);text-transform:uppercase}.dot{display:inline-block;width:8px;height:8px;border-radius:100%;background:#209484;margin-right:7px}h1{font-size:clamp(2.2rem,5.1vw,4.4rem);line-height:1.1;letter-spacing:-.06em;max-width:820px;margin:17px 0}h2{font-size:1.45rem;line-height:1.3;letter-spacing:-.03em;margin:28px 0 12px}h3{font-size:1.05rem;margin:18px 0 6px}
.hero-lede{max-width:760px;font-size:clamp(1rem,1.7vw,1.2rem);color:#536078;margin-bottom:25px}.hero-actions{display:flex;gap:20px;align-items:center;flex-wrap:wrap}.cta{display:inline-block;background:var(--accent);color:#fff!important;text-decoration:none;border-radius:11px;padding:12px 18px;margin:12px 0;font-weight:750}.cta:hover{background:#3a285e}.text-link{font-weight:750}.hero-metrics{display:flex;gap:35px;flex-wrap:wrap;margin-top:25px;padding-top:24px;border-top:1px solid #cec8db}.hero-metrics div{display:flex;flex-direction:column}.hero-metrics strong{font-size:1.65rem;letter-spacing:-.05em;color:var(--accent);line-height:1.2}.hero-metrics span{font-size:.81rem;color:var(--muted)}
.catalogue{margin-top:50px}.section-intro{display:flex;justify-content:space-between;align-items:end;gap:18px;flex-wrap:wrap;margin-bottom:20px}.section-intro h2{margin:6px 0;font-size:clamp(1.6rem,3vw,2.1rem)}.section-intro p{color:var(--muted);margin:0}.program-search{border-radius:11px;border:1px solid #cfd5e2;background:#fff;padding:12px 15px;font:inherit;min-width:min(300px,82vw)}.result-status{font-size:.86rem;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:17px}.program-card{background:#fff;border:1px solid var(--line);border-radius:17px;padding:23px;box-shadow:0 5px 25px #17233908;transition:transform .15s}.program-card:hover{transform:translateY(-3px)}.program-card[hidden]{display:none}.program-card h2{font-size:1.55rem;margin:12px 0 8px}.program-card p{color:var(--muted);font-size:.89rem}.country-links{display:flex;flex-wrap:wrap;gap:8px}.country-link{background:#eeeaf8;padding:7px 10px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.83rem}
.workflow-note{margin-top:40px;background:#fff;border:1px solid var(--line);border-radius:20px;padding:25px}.workflow-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.workflow-grid>div{padding:16px;background:var(--bg);border-radius:12px}.workflow-grid p{color:var(--muted);font-size:.86rem}
.detail-intro{background:linear-gradient(120deg,#f1ecfa,#e6f4f2);border-radius:22px;padding:32px}.detail-intro h1{font-size:clamp(2rem,4vw,3.4rem)}nav.crumbs{font-size:.83rem;color:var(--muted);margin:12px 0}dl.facts{display:grid;grid-template-columns:170px 1fr;gap:12px 20px;background:#fff;border:1px solid var(--line);padding:24px;border-radius:16px;max-width:840px}dl.facts dt{color:var(--muted)}dl.facts dd{margin:0;font-weight:750}.meta{color:var(--muted);font-size:.83rem}ul.links{padding-left:22px}
.site-footer{background:#fff;border-top:1px solid var(--line)}.footer-inner{max-width:1190px;margin:auto;padding:24px 28px;display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;color:var(--muted);font-size:.83rem}
@media(max-width:700px){main{padding:20px 15px 50px}.nav-wrap{padding:12px 15px}.site-nav a:first-child{display:none}.hero{padding:28px 22px}.workflow-grid{grid-template-columns:1fr}.detail-intro{padding:22px}dl.facts{grid-template-columns:1fr;gap:2px}dl.facts dd{margin-bottom:12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.program-card{transition:none}}
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
<a class="skip-link" href="#main">Skip to content</a>
<header class="site"><div class="nav-wrap"><a class="brand" href="{PREFIX}/"><span class="brand-mark">K</span>{esc(SITE)}</a><nav class="site-nav" aria-label="Primary navigation"><a href="{PREFIX}/">Home</a><a class="nav-cta" href="{PREFIX}/programmes/">Programmes</a></nav></div></header>
<main id="main">
"""


FOOT = """
</main>
<footer class="site-footer"><div class="footer-inner"><span>Fictional education demo created to test programmatic and technical SEO.</span><a href="https://github.com/graceomolola001-cmyk/kestrel-pseo">View source code ↗</a></div></footer>
<script>
document.addEventListener("DOMContentLoaded", function () {
  var input = document.querySelector("[data-programme-search]");
  if (!input) return;
  var cards = Array.from(document.querySelectorAll("[data-programme-card]"));
  var status = document.querySelector("[data-results-status]");
  function update() {
    var term = input.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {
      var matches = card.getAttribute("data-search").toLowerCase().includes(term);
      card.hidden = !matches;
      if (matches) shown++;
    });
    if (status) status.textContent = shown + " programme group" + (shown === 1 ? "" : "s") + " shown";
  }
  input.addEventListener("input", update);
  update();
});
</script>
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
    body = f"""<div class="detail-intro"><div class="eyebrow">FICTIONAL PROGRAMME PROFILE</div><nav class="crumbs" aria-label="Breadcrumb"><a href="{PREFIX}/">Home</a> / <a href="{PREFIX}/programmes/">Programmes</a> / {esc(n)}</nav>
<h1>{esc(n)}</h1>
<p class="hero-lede">An illustrative programme page for {esc(r["country"])}. All fees, dates and admission details are fictional.</p></div>
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
<a class="cta" href="{PREFIX}/programmes/">Browse other demo programmes ↗</a>
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
        matches = [x for x in pub if x["programme"] == p]
        links = "".join(
            f'<a class="country-link" href="{PREFIX}{path_for(x)}">{esc(x["country"])} ↗</a>'
            for x in matches
        )
        searchable = p + " " + " ".join(x["country"] for x in matches)
        cells += (
            f'<article class="program-card" data-programme-card data-search="{esc(searchable)}">'
            f'<div class="card-flag">PROGRAMME COLLECTION</div>'
            f'<h2>{esc(p)}</h2>'
            f'<p>Fictional programme examples for {len(matches)} countries.</p>'
            f'<div class="country-links">{links}</div></article>'
        )
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
    body = f"""<section class="hero">
<div class="eyebrow"><span class="dot" aria-hidden="true"></span> TECHNICAL SEO ENGINEERING DEMONSTRATION</div>
<h1>{esc(h1)}</h1>
<p class="hero-lede">Explore a fictional education website generated from structured source records. This project demonstrates programmatic SEO, automated technical checks and repeatable quality assurance. Programme information here is illustrative and does not represent a real admissions offer.</p>
<div class="hero-actions"><a class="cta" href="#catalogue">Explore the catalogue ↗</a><a class="text-link" href="https://github.com/graceomolola001-cmyk/kestrel-pseo">Review the Python code</a></div>
<div class="hero-metrics"><div><strong>{len(pub)}</strong><span>Programme records</span></div><div><strong>{len(progs)}</strong><span>Subject groups</span></div><div><strong>3</strong><span>Build, validate, monitor</span></div></div>
</section>
<section class="catalogue" id="catalogue" aria-label="Programme catalogue">
<div class="section-intro"><div><div class="eyebrow">BROWSE THE DATASET</div><h2>Explore the programme catalogue</h2><p>Filter by programme or country to explore the generated pages.</p></div><label><span class="eyebrow">FILTER PROGRAMMES</span><input class="program-search" type="search" data-programme-search placeholder="Search by programme or country" autocomplete="off"></label></div>
<p class="result-status" data-results-status role="status" aria-live="polite">{len(progs)} programme groups shown</p>
<div class="grid">{cells}</div></section>
<section class="workflow-note"><div class="eyebrow">ENGINEERING APPROACH</div><h2>Built for reliable, repeatable SEO checks</h2><div class="workflow-grid">
<div><b>01 / Generate</b><p>Python turns structured programme records into consistent HTML pages.</p></div>
<div><b>02 / Validate</b><p>Automated QA checks page metadata, links, canonicals and JSON-LD.</p></div>
<div><b>03 / Monitor</b><p>A scheduled crawler produces structured, actionable SEO health reports.</p></div>
</div></section>
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
    # Allow crawling so the page-level noindex directive can be discovered.
    # For GitHub project pages, host-root robots.txt is controlled separately.
    robots = "User-agent: *\nAllow: /\n"
    if not noindex:
        robots += f"Sitemap: {a.base_url.rstrip('/')}/sitemap.xml\n"
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
