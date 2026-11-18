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
<header class="site"><div class="nav-wrap"><a class="brand" href="{PREFIX}/"><span class="brand-mark" aria-hidden="true">K.</span><span>Kestrel <small>SEO OPERATIONS LAB</small></span></a><nav class="site-nav" aria-label="Primary navigation"><a href="{PREFIX}/">Home</a><a href="{PREFIX}/systems/">How it works</a><a href="{PREFIX}/lab/">Try the lab</a><a href="{PREFIX}/reports/">Reports</a><a class="nav-cta" href="{PREFIX}/programmes/">Pages ↗</a></nav></div></header>
<main id="main">
"""


FOOT = """
</main>
<footer class="site-footer"><div class="footer-inner"><span>KESTREL SEO OPERATIONS LAB / Fictional education data used for engineering demonstrations.</span><span><a href="{PREFIX}/systems/">How it works</a> · <a href="{PREFIX}/lab/">Try the lab</a> · <a href="{PREFIX}/reports/">Reports</a> · <a href="https://github.com/graceomolola001-cmyk/kestrel-pseo">GitHub ↗</a></span></div></footer>
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
<div class="eyebrow section-index">SAMPLE COURSE / MADE-UP DATA</div>
<nav class="crumbs" aria-label="Breadcrumb"><a href="{PREFIX}/">Home</a> / <a href="{PREFIX}/programmes/">Catalogue</a> / {esc(n)}</nav>
<h1>{esc(n)}</h1>
<p class="hero-lede">A sample course page for {esc(r["country"])}. The fees, dates, and entry rules are made up. This page helps show how the website tools work.</p>
</div>
<div class="detail-cols">
<article class="detail-main" data-reveal>
<div class="eyebrow section-index">01 / COURSE DETAILS</div>
<h2>Course details</h2>
<dl class="facts">
<dt>Fees</dt><dd data-field="fees">{esc(r['fees'])}</dd>
<dt>Duration</dt><dd data-field="duration">{esc(r['duration'])}</dd>
<dt>Next intake</dt><dd data-field="intake">{esc(r['intake'])}</dd>
<dt>Entry requirements</dt><dd data-field="entry">{esc(r['entry'])}</dd>
</dl>
<p class="meta">Sample source: {esc(r['source'])}. Sample check date: {esc(r['last_verified'])}.</p>
<div class="eyebrow section-index" style="margin-top:52px">02 / WHO IT IS FOR</div>
<h2>Who this course may suit</h2>
<p data-field="suits">{esc(r['suits'])}</p>
<div class="eyebrow section-index" style="margin-top:48px">03 / USEFUL LINKS</div>
<h2>Common questions</h2>
<div>{qa_html}</div>
<h2>Related course pages</h2>
{related(r, pub)}
<a class="cta" href="{PREFIX}/programmes/">Back to course list ↗</a>
</article>
<aside class="side-note" data-reveal>
<div class="eyebrow">HOW THIS PAGE WAS MADE</div>
<h3>One layout. Many course pages.</h3>
<p>Python builds this page from a row in a table. Before it goes live, Kestrel checks its title, links, and SEO tags.</p>
<p>This sample page has a noindex tag. That tells Google not to show it in search results.</p>
<a class="board-link" href="https://github.com/graceomolola001-cmyk/kestrel-pseo/blob/main/build.py">See the Python code ↗</a>
</aside>
</div>
{ld}"""
    return head(title, meta_description(r), canonical, noindex) + body + FOOT.replace("{PREFIX}", PREFIX)

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
            f'<div class="card-flag">SAMPLE / {len(matches):02d} COUNTRIES</div>'
            f'<h3>{esc(p)}</h3>'
            f'<p>See the sample course pages for each country.</p>'
            f'<div class="country-links">{links}</div></article>'
        )
    controls = '<button type="button" class="market-filter" data-market-filter="all" aria-pressed="true">All markets</button>'
    controls += "".join(
        f'<button type="button" class="market-filter" data-market-filter="{esc(c.lower())}" aria-pressed="false">{esc(c)}</button>'
        for c in markets
    )
    catalogue = f"""<section class="catalogue" id="catalogue" aria-label="Programme catalogue" data-reveal>
<div class="section-intro"><div><div class="eyebrow section-index">02 / COURSE PAGES</div>
<h2>Explore the <em>course pages.</em></h2>
<p>See {len(pub)} sample course pages across {len(markets)} countries. Python builds each page and checks it before it goes live.</p></div></div>
<div class="filter-row"><input class="program-search" type="search" data-programme-search aria-label="Search programmes" placeholder="Find a course or country…" autocomplete="off">
<div class="market-filters" role="group" aria-label="Filter by market">{controls}</div></div>
<p class="result-status" data-results-status role="status" aria-live="polite">{len(progs)} programme groups shown</p>
<div class="grid">{cells}</div>
<p class="empty-state" data-empty-state hidden>No courses found. Try another word or country.</p>
</section>"""
    if home:
        title = f"Kestrel: simple SEO tools and live site checks"
        desc = ("Try Kestrel's sample SEO website, "
                "live site checks, and easy-to-read reports.")
        canonical = base.rstrip("/") + "/"
        hero = f"""<section class="hero" aria-label="Kestrel lab introduction">
<div class="hero-copy" data-reveal>
<div class="eyebrow section-index">CASE FILE 001 / SEO TOOLS</div>
<h1>Find SEO problems <em>before they grow.</em></h1>
<p class="hero-lede">Meet a website built to find SEO mistakes early. See how pages are made, checked, and watched after they go live. Try the tools yourself.</p>
<div class="hero-actions"><a class="cta" href="{PREFIX}/lab/">Try the SEO lab ↗</a>
<a class="cta-outline" href="{PREFIX}/programmes/">Explore the pages</a></div>
<p class="hero-footnote">The school and courses are made up. The code and site checks are real. You can see how they work.</p>
</div>
<aside class="status-board" data-audit-feed="{PREFIX}/seo-health.json" aria-label="Actual published SEO audit" data-reveal>
<div class="board-head"><span>KESTREL / RELEASE AUDIT</span><span class="indicator">REAL TEST DATA</span></div>
<div class="board-canvas">
<svg class="circuit" viewBox="0 0 390 230" preserveAspectRatio="none" role="img" aria-label="Animated symbolic data pipeline">
<path d="M20 40 H120 L160 96 H220 L275 40 H370 M20 195 H125 L170 136 H220 L280 195 H370"/>
<path class="accent-path" d="M16 115 H132 L185 115 H365"/>
<circle cx="18" cy="115" r="4"/><circle cx="364" cy="115" r="4"/>
</svg>
<span class="circuit-label top">01 / BUILD</span>
<span class="circuit-label right">02 / CHECK</span>
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
<div class="ticker-track" aria-hidden="true"><span>Build pages from a table</span><span>Check pages before they go live</span><span>Check the live site</span><span>Build pages from a table</span><span>Check pages before they go live</span></div></div>
<section class="section" aria-label="How Kestrel operates" data-reveal>
<div class="section-heading"><div><div class="eyebrow section-index">01 / HOW IT WORKS</div><h2>Catch the mistakes<br><em>you can't always see.</em></h2></div>
<p>One small mistake can affect many pages. Kestrel checks for common errors before a page goes live. It also creates clear reports so teams know what to fix.</p></div>
<div class="workflow-grid">
<article class="workflow-step"><div class="step-no">01 / BUILD</div><h3>Start with the page details.</h3><p>A simple table holds the page details. Python turns that table into real HTML pages with titles and links.</p></article>
<article class="workflow-step"><div class="step-no">02 / CHECK</div><h3>Test before going live.</h3><p>The site checks page titles, links, page addresses, and code before each release. A serious error can stop the release.</p></article>
<article class="workflow-step"><div class="step-no">03 / MONITOR</div><h3>Check again after launch.</h3><p>A crawler checks the live site and writes a report. A person reviews the issues and decides what to fix.</p></article>
</div></section>
"""

        routes = f"""<section class="section" data-reveal aria-label="Explore the SEO lab">
<div class="eyebrow section-index">EXPLORE KESTREL</div><h2>Take a look <em>inside.</em></h2>
<div class="route-grid">
<a class="route-card" href="{PREFIX}/systems/"><small>01 / THE SYSTEM</small><b>How does it work?</b><span>Follow the steps from page data to a live website.</span><small>SEE THE STEPS ↗</small></a>
<a class="route-card" href="{PREFIX}/lab/"><small>02 / TRY IT</small><b>Can you spot the error?</b><span>Try three real kinds of SEO mistakes in a safe demo.</span><small>OPEN THE LAB ↗</small></a>
<a class="route-card" href="{PREFIX}/reports/"><small>03 / THE PROOF</small><b>What did the checks find?</b><span>See the results from the site's latest build.</span><small>VIEW REPORTS ↗</small></a>
</div></section>"""
        body = hero + routes
    else:
        title = f"Programme catalogue | {SITE} SEO lab"
        desc = "Explore sample course pages made by Python and checked for SEO mistakes."
        canonical = base.rstrip("/") + "/programmes/"
        lead = """<section class="collection-head" data-reveal><div><div class="eyebrow section-index">INDEX / GENERATED PAGES</div>
<h1>The course page library.</h1></div><p>These sample course pages come from one table. Search or choose a country to see how Python builds different pages from the same layout.</p></section>"""
        body = lead + catalogue
    return head(title, desc, canonical, noindex) + body + FOOT.replace("{PREFIX}", PREFIX)

def section_page(section, base, noindex, pub):
    """Standalone sections with their own URLs, canonicals and page copy."""
    titles = {
        "systems": ("How Kestrel checks SEO pages | Kestrel",
                    "Follow the steps Kestrel uses to make pages, test them and find errors."),
        "lab": ("Try the SEO error lab | Kestrel",
                "Try simple examples of noindex, wrong canonical URLs and broken links."),
        "reports": ("Live SEO reports and checks | Kestrel",
                    "See what Kestrel's real page tests found.")
    }
    title, desc = titles[section]
    canonical = base.rstrip("/") + f"/{section}/"
    experiment = """<section class="experiment" id="diagnostics" aria-label="Interactive technical SEO diagnostics" data-reveal>
<div class="eyebrow section-index">INTERACTIVE LAB / PRACTICE EXAMPLES</div>
<h2>Pick a problem.<br><em>See how to catch it.</em></h2>
<p class="experiment-lede">Try three common website errors. Click one to see what went wrong, why it matters, and what to check next.</p>
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
    board = f"""<aside class="status-board" data-audit-feed="{PREFIX}/seo-health.json" aria-label="Actual published SEO audit" data-reveal>
<div class="board-head"><span>KESTREL / RELEASE AUDIT</span><span class="indicator">REAL TEST DATA</span></div>
<div class="board-canvas">
<svg class="circuit" viewBox="0 0 390 230" preserveAspectRatio="none" role="img" aria-label="Animated symbolic data pipeline">
<path d="M20 40 H120 L160 96 H220 L275 40 H370 M20 195 H125 L170 136 H220 L280 195 H370"/>
<path class="accent-path" d="M16 115 H132 L185 115 H365"/>
<circle cx="18" cy="115" r="4"/><circle cx="364" cy="115" r="4"/>
</svg>
<span class="circuit-label top">01 / BUILD</span>
<span class="circuit-label right">02 / CHECK</span>
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
</aside>"""
    if section == "systems":
        content = f"""<section class="section-landing" data-reveal>
<div class="eyebrow section-index">01 / HOW IT WORKS</div>
<h1>From a table<br>to a <em>tested website.</em></h1>
<p class="hero-lede">Kestrel starts with a table. Python makes the pages. Then tests look for mistakes before the site goes live. Here's how each part works.</p></section>
<section class="page-guide" data-reveal><div class="eyebrow">FOUR SIMPLE STEPS</div>
<ol class="process-list">
<li><div><strong>Collect the page details</strong><p>A CSV is like a spreadsheet. It holds each course name, country, fee, and start date. Kestrel checks every row before it builds a page.</p></div></li>
<li><div><strong>Make the HTML pages</strong><p>Python uses one shared template to build every page. It also adds page titles, descriptions, and links to related pages.</p></div></li>
<li><div><strong>Check the work before release</strong><p>The tests look for broken links, missing details, and wrong SEO tags. If a serious check fails, GitHub stops the update.</p></div></li>
<li><div><strong>Check the live site again</strong><p>A crawler is a tool that visits pages. It checks the live site on a schedule, then saves a report for people and software to read.</p></div></li>
</ol>
<div class="proof-note"><strong>What you should know:</strong> The course details are made up. The code and test results are real. The sample pages have a noindex tag, which tells Google to leave them out of search.</div>
<div class="proof-links"><a class="cta" href="{PREFIX}/reports/">See the audit results ↗</a><a class="cta-outline" href="https://github.com/graceomolola001-cmyk/kestrel-pseo/blob/main/build.py">Read the Python code ↗</a></div>
</section>"""
    elif section == "lab":
        content = f"""<section class="section-landing" data-reveal>
<div class="eyebrow section-index">02 / TRY THE LAB</div>
<h1>What happens when<br><em>a page has an SEO error?</em></h1>
<p class="hero-lede">A page can look fine but still have an SEO mistake in its code. Pick an example to see what went wrong.</p></section>
{experiment}
<div class="page-guide"><div class="proof-note"><strong>These are practice examples.</strong> They do not change or scan the live site. To see results from Kestrel's real tests, open the reports page.</div>
<a class="cta" href="{PREFIX}/reports/">View the real reports ↗</a></div>"""
    elif section == "reports":
        content = f"""<section class="section-landing" data-reveal>
<div class="eyebrow section-index">03 / THE RESULTS</div>
<h1>Show the work.<br><em>Show the checks.</em></h1>
<p class="hero-lede">This page reads Kestrel's real test report. It shows how many pages were checked and how many errors the tests found.</p></section>
<section class="report-panel" data-reveal>{board}</section>
<section class="page-guide" data-reveal><div class="eyebrow">WHAT THE REPORT MEANS</div>
<h2>Proof you can <em>check yourself.</em></h2>
<p>The report checks page code and SEO tags. A clean report means those checks passed. It doesn't tell us if Google shows or ranks the pages.</p>
<div class="proof-links"><a class="cta" href="{base.rstrip('/')}/seo-health.html">Open the full report ↗</a>
<a class="cta-outline" href="https://github.com/graceomolola001-cmyk/kestrel-pseo/actions">See build runs on GitHub ↗</a></div></section>"""
    return head(title, desc, canonical, noindex) + content + FOOT.replace("{PREFIX}", PREFIX)


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
    for section in ("systems", "lab", "reports"):
        write(f"/{section}/index.html", section_page(section, a.base_url, noindex, pub))
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
