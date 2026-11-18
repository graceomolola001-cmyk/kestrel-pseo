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
GA4_MEASUREMENT_ID = ""
GSC_VERIFICATION_TOKEN = ""
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
    verification_tag = (
        f'<meta name="google-site-verification" content="{esc(GSC_VERIFICATION_TOKEN)}">'
        if GSC_VERIFICATION_TOKEN else ""
    )
    analytics_tag = ""
    if GA4_MEASUREMENT_ID:
        # Google tag ID is a public web-stream identifier, never a credential.
        tag_id_json = json.dumps(GA4_MEASUREMENT_ID)
        analytics_tag = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {{ dataLayer.push(arguments); }}
  gtag('js', new Date());
  gtag('config', {tag_id_json});
</script>"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(canonical)}">
{verification_tag}
{analytics_tag}
<link rel="stylesheet" href="{PREFIX}/assets/site.css">
<script defer src="{PREFIX}/assets/site.js"></script>
</head>
<body>
<div class="lab-ribbon"><span>KESTREL / SEO SYSTEMS FIELD NOTES <strong>★ LAB EDITION</strong></span><span>OPEN SOURCE · FICTIONAL DATASET</span></div>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site"><div class="nav-wrap"><a class="brand" href="{PREFIX}/"><span class="brand-mark" aria-hidden="true">K.</span><span>Kestrel <small>SEO OPERATIONS LAB</small></span></a><nav class="site-nav" aria-label="Primary navigation"><a href="{PREFIX}/">Home</a><a href="{PREFIX}/#laboratory">The lab</a><a class="nav-cta" href="{PREFIX}/programmes/">Browse pages ↗</a></nav></div></header>
<main id="main">
"""


FOOT = """
</main>
<footer class="site-footer"><div class="footer-inner"><span>KESTREL SEO OPERATIONS LAB / Fictional education data used for engineering demonstrations.</span><span><a href="https://github.com/graceomolola001-cmyk/kestrel-pseo">Source code ↗</a> · <a href="https://github.com/graceomolola001-cmyk/kestrel-pseo/actions">Build evidence ↗</a></span></div></footer>
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
    qa_html = "".join(
        f'<details class="qa-item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for q, a in qa
    )
    ld = ""
    if faq_schema:
        data = {"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q,
                                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
        ld = f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    body = f"""<div class="detail-intro" data-reveal>
<div class="eyebrow section-index">DATA RECORD / FICTIONAL PROGRAMME</div>
<nav class="crumbs" aria-label="Breadcrumb"><a href="{PREFIX}/">Home</a> / <a href="{PREFIX}/programmes/">Catalogue</a> / {esc(n)}</nav>
<h1>{esc(n)}</h1>
<p class="hero-lede">A generated programme profile for {esc(r["country"])}. Fees, dates and admissions details are entirely fictional and used only to demonstrate the SEO publishing workflow.</p>
</div>
<div class="detail-cols">
<article class="detail-main" data-reveal>
<div class="eyebrow section-index">01 / STRUCTURED SOURCE</div>
<h2>Programme facts</h2>
<dl class="facts">
<dt>Fees</dt><dd data-field="fees">{esc(r['fees'])}</dd>
<dt>Duration</dt><dd data-field="duration">{esc(r['duration'])}</dd>
<dt>Next intake</dt><dd data-field="intake">{esc(r['intake'])}</dd>
<dt>Entry requirements</dt><dd data-field="entry">{esc(r['entry'])}</dd>
</dl>
<p class="meta">Illustrative source: {esc(r['source'])}. Example verification date: {esc(r['last_verified'])}.</p>
<div class="eyebrow section-index" style="margin-top:52px">02 / AUDIENCE INTENT</div>
<h2>Who this page is written for</h2>
<p data-field="suits">{esc(r['suits'])}</p>
<div class="eyebrow section-index" style="margin-top:48px">03 / INFORMATION ARCHITECTURE</div>
<h2>Common questions</h2>
<div>{qa_html}</div>
<h2>Related programme pages</h2>
{related(r, pub)}
<a class="cta" href="{PREFIX}/programmes/">Back to catalogue ↗</a>
</article>
<aside class="side-note" data-reveal>
<div class="eyebrow">THE ENGINEERING BEHIND THIS PAGE</div>
<h3>One template. Structured facts. Repeatable checks.</h3>
<p>Python renders this page from a source record. Pre-release checks inspect metadata, canonical signals, internal navigation and schema where configured.</p>
<p>These fictional records are marked noindex by design, and page-level metadata is available for inspection.</p>
<a class="board-link" href="https://github.com/graceomolola001-cmyk/kestrel-pseo/blob/main/build.py">Inspect the generator ↗</a>
</aside>
</div>
{ld}"""
    return head(title, meta_description(r), canonical, noindex) + body + FOOT

def hub(pub, base, noindex, home=False):
    progs = list(dict.fromkeys(r["programme"] for r in pub))
    markets = sorted(set(r["country"] for r in pub))
    cells = ""
    for p in progs:
        matches = [x for x in pub if x["programme"] == p]
        links = "".join(
            f'<a class="country-link" href="{PREFIX}{path_for(x)}">{esc(x["country"])} ↗</a>'
            for x in matches
        )
        searchable = p + " " + " ".join(x["country"] for x in matches)
        market_names = "|".join(x["country"].lower() for x in matches)
        cells += (
            f'<article class="program-card" data-programme-card data-search="{esc(searchable)}" data-markets="{esc(market_names)}">'
            f'<div class="card-flag">RECORD / {len(matches):02d} MARKETS</div>'
            f'<h3>{esc(p)}</h3>'
            f'<p>Browse the fictional, location-specific records generated from one template.</p>'
            f'<div class="country-links">{links}</div></article>'
        )
    controls = '<button type="button" class="market-filter" data-market-filter="all" aria-pressed="true">All markets</button>'
    controls += "".join(
        f'<button type="button" class="market-filter" data-market-filter="{esc(c.lower())}" aria-pressed="false">{esc(c)}</button>'
        for c in markets
    )
    catalogue = f"""<section class="catalogue" id="catalogue" aria-label="Programme catalogue" data-reveal>
<div class="section-intro"><div><div class="eyebrow section-index">02 / STRUCTURED PAGES</div>
<h2>Explore the <em>dataset.</em></h2>
<p>One source inventory, {len(pub)} sample programme records, {len(markets)} markets. Every programme page is generated by Python and validated before publication.</p></div></div>
<div class="filter-row"><input class="program-search" type="search" data-programme-search aria-label="Search programmes" placeholder="Search topic or market…" autocomplete="off">
<div class="market-filters" role="group" aria-label="Filter by market">{controls}</div></div>
<p class="result-status" data-results-status role="status" aria-live="polite">{len(progs)} programme groups shown</p>
<div class="grid">{cells}</div>
<p class="empty-state" data-empty-state hidden>No matching programme groups. Try a different search or market.</p>
</section>"""
    if home:
        title = f"Kestrel: interactive technical SEO and automation lab"
        desc = ("Explore Kestrel's interactive, fictional programmatic SEO site, "
                "live technical audit and automated release validation.")
        canonical = base.rstrip("/") + "/"
        hero = f"""<section class="hero" aria-label="Kestrel lab introduction">
<div class="hero-copy" data-reveal>
<div class="eyebrow section-index">CASE FILE 001 / ENGINEERED SEO</div>
<h1>Good SEO needs <em>good systems.</em></h1>
<p class="hero-lede">A small, independent engineering lab for the parts of SEO that deserve more than a manual checklist. Generate pages. Catch mistakes before release. Make the evidence easy to read.</p>
<div class="hero-actions"><a class="cta" href="#laboratory">Try the diagnostic lab ↗</a>
<a class="cta-outline" href="#catalogue">Explore generated pages</a></div>
<p class="hero-footnote">The education website, programmes and course details are fictional. The code, deployment process and automated SEO checks are real.</p>
</div>
<aside class="status-board" data-audit-feed="{PREFIX}/seo-health.json" aria-label="Actual published SEO audit" data-reveal>
<div class="board-head"><span>KESTREL / RELEASE AUDIT</span><span class="indicator">SOURCE: PUBLISHED JSON</span></div>
<div class="board-canvas">
<svg class="circuit" viewBox="0 0 390 230" preserveAspectRatio="none" role="img" aria-label="Animated symbolic data pipeline">
<path d="M20 40 H120 L160 96 H220 L275 40 H370 M20 195 H125 L170 136 H220 L280 195 H370"/>
<path class="accent-path" d="M16 115 H132 L185 115 H365"/>
<circle cx="18" cy="115" r="4"/><circle cx="364" cy="115" r="4"/>
</svg>
<span class="circuit-label top">01 / GENERATE</span>
<span class="circuit-label right">02 / VALIDATE</span>
<span class="circuit-label bottom">03 / REPORT</span>
<div class="circuit-center" aria-hidden="true"><strong>K.</strong></div>
</div>
<div class="board-stats"><div class="board-kicker">DEPLOYED RELEASE / REAL REPORT</div>
<div class="board-stat-grid"><div><strong data-audit-pages>…</strong><span>Pages checked</span></div>
<div><strong data-audit-errors>…</strong><span>Errors reported</span></div></div>
<p class="board-status" data-audit-status role="status">Reading the published audit…</p>
<p class="board-status" data-audit-footnote></p>
<a class="board-link" href="{base.rstrip('/')}/seo-health.html">Open the audit evidence ↗</a>
</div>
</aside>
</section>
<div class="ticker" aria-label="Generate, validate and monitor"><span class="ticker-label">WORKFLOW</span>
<div class="ticker-track" aria-hidden="true"><span>Generate from structured data</span><span>Validate before publishing</span><span>Monitor the live output</span><span>Generate from structured data</span><span>Validate before publishing</span></div></div>
<section class="section" aria-label="How Kestrel operates" data-reveal>
<div class="section-heading"><div><div class="eyebrow section-index">01 / HOW IT WORKS</div><h2>Built to catch<br><em>the quiet mistakes.</em></h2></div>
<p>A broken canonical or a stray noindex can affect hundreds of pages. Kestrel applies predictable rules at publish time, then generates reports people can actually act on.</p></div>
<div class="workflow-grid">
<article class="workflow-step"><div class="step-no">01 / GENERATE</div><h3>Start with the source.</h3><p>Structured records power the HTML templates, page titles, metadata and contextual internal links.</p></article>
<article class="workflow-step"><div class="step-no">02 / VALIDATE</div><h3>Make the build prove itself.</h3><p>Python checks data quality, generated HTML, canonical patterns, schema and redirect rules before deployment.</p></article>
<article class="workflow-step"><div class="step-no">03 / MONITOR</div><h3>Keep watching after launch.</h3><p>Bounded crawls and structured reports surface technical issues for a human to investigate.</p></article>
</div></section>
<section class="experiment" id="laboratory" aria-label="Interactive technical SEO diagnostics" data-reveal>
<div class="eyebrow section-index">INTERACTIVE LAB / SYNTHETIC EXAMPLES</div>
<h2>Break something.<br><em>See what gets caught.</em></h2>
<p class="experiment-lede">Choose a common technical SEO failure. This interactive simulation explains how a rules-based checker could identify it and what an SEO specialist should investigate next.</p>
<div class="lab-shell">
<div class="scenario-controls" role="tablist" aria-label="Choose an example SEO failure">
<h3>SELECT A FAILURE</h3>
<button type="button" role="tab" class="scenario-tab" data-scenario="noindex" aria-selected="true" aria-controls="scenario-panel">01 / Accidental noindex</button>
<button type="button" role="tab" class="scenario-tab" data-scenario="canonical" aria-selected="false" aria-controls="scenario-panel" tabindex="-1">02 / Wrong canonical</button>
<button type="button" role="tab" class="scenario-tab" data-scenario="link" aria-selected="false" aria-controls="scenario-panel" tabindex="-1">03 / Broken internal link</button>
</div>
<div class="scenario-output" id="scenario-panel" role="tabpanel" aria-live="polite">
<span class="scenario-location" data-scenario-path>/programmes/online-mba-ghana/</span>
<pre class="scenario-code"><code data-scenario-code>&lt;meta name="robots" content="noindex"&gt;</code></pre>
<div class="scenario-finding"><strong data-scenario-level>CRITICAL · INDEXABILITY</strong>
<h3 data-scenario-title>An important page is excluded</h3>
<p data-scenario-explanation>A crawler can flag unexpected noindex directives against an approved baseline.</p></div>
</div></div>
<p class="lab-caption">SIMULATION ONLY · These examples are predefined teaching fixtures and are not findings from the live Kestrel site. Real findings appear in the published audit above.</p>
</section>"""
        body = hero + catalogue
    else:
        title = f"Programme catalogue | {SITE} SEO lab"
        desc = "Browse generated and validated fictional programme pages in the Kestrel SEO engineering demonstration."
        canonical = base.rstrip("/") + "/programmes/"
        lead = """<section class="collection-head" data-reveal><div><div class="eyebrow section-index">INDEX / GENERATED PAGES</div>
<h1>The page library.</h1></div><p>Fictional programme records, generated from a shared template. Use the filters to explore how one validated dataset becomes a linked page collection.</p></section>"""
        body = lead + catalogue
    return head(title, desc, canonical, noindex) + body + FOOT

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/pages.csv")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--base-url", default="https://example.com")
    ap.add_argument("--index", action="store_true", help="allow indexing and write sitemap.xml")
    ap.add_argument("--faq-schema", action="store_true", help="write FAQPage JSON-LD")
    a = ap.parse_args()
    global PREFIX, GA4_MEASUREMENT_ID, GSC_VERIFICATION_TOKEN
    PREFIX = urlparse(a.base_url).path.rstrip("/")
    GA4_MEASUREMENT_ID = os.environ.get("KESTREL_GA4_MEASUREMENT_ID", "").strip()
    GSC_VERIFICATION_TOKEN = os.environ.get("KESTREL_GSC_VERIFICATION_TOKEN", "").strip()
    if GA4_MEASUREMENT_ID and not re.fullmatch(r"G-[A-Z0-9]{5,20}", GA4_MEASUREMENT_ID):
        print("Build stopped: KESTREL_GA4_MEASUREMENT_ID must be a GA4 web stream ID starting with G-")
        return 2
    if GSC_VERIFICATION_TOKEN and not re.fullmatch(r"[A-Za-z0-9_+=/-]{8,256}", GSC_VERIFICATION_TOKEN):
        print("Build stopped: expected only the HTML verification tag content, not the full meta tag")
        return 2

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

    # Keep styles and interactions as separate, cacheable static assets.
    asset_dir = os.path.join(a.out, "assets")
    os.makedirs(asset_dir, exist_ok=True)
    for filename in ("site.css", "site.js"):
        shutil.copyfile(os.path.join("site_assets", filename),
                        os.path.join(asset_dir, filename))

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
