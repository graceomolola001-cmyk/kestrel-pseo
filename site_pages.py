"""Generated editorial sections for the Kestrel SEO Operations Lab.

The marketing site is intentionally fictional. Architecture, code, and audit
evidence link to actual project assets. No client data or private credentials.
"""


def render_pages(head, footer, base_url, prefix, noindex, record_count, market_count):
    """Return {URL path: complete HTML} for the standalone lab site pages."""
    base = base_url.rstrip("/")
    repo = "https://github.com/graceomolola001-cmyk/kestrel-pseo"
    def link(path):
        return prefix + path

    def page(path, title, description, body):
        canonical = base + path
        return head(title, description, canonical, noindex) + body + footer

    def kicker(text):
        return f'<div class="eyebrow section-index">{text}</div>'

    def breadcrumb(items):
        bits = [f'<a href="{link("/")}">Overview</a>']
        for label, href in items[:-1]:
            bits.append(f'<a href="{link(href)}">{label}</a>')
        bits.append(items[-1][0])
        return '<nav class="crumbs" aria-label="Breadcrumb">' + ' / '.join(bits) + '</nav>'

    def section_card(num, title, description, path, note):
        return f"""<a class="route-card" href="{link(path)}" data-reveal>
<span class="route-card-top"><span class="overline">{num}</span><span class="route-card-arrow" aria-hidden="true">↗</span></span>
<strong>{title}</strong><span class="route-card-desc">{description}</span>
<span class="route-card-note">{note}</span></a>"""

    board = f"""<aside class="status-board" data-audit-feed="{link('/seo-health.json')}" aria-label="Published build-time SEO audit" data-reveal>
<div class="board-head"><span>KESTREL / RELEASE AUDIT</span><span class="indicator">ACTUAL BUILD REPORT</span></div>
<div class="board-canvas">
<svg class="circuit" viewBox="0 0 390 230" preserveAspectRatio="none" role="img" aria-label="Symbolic pipeline connecting generation, checks and reports">
<path d="M20 40 H120 L160 96 H220 L275 40 H370 M20 195 H125 L170 136 H220 L280 195 H370"/>
<path class="accent-path" d="M16 115 H132 L185 115 H365"/>
<circle cx="18" cy="115" r="4"/><circle cx="364" cy="115" r="4"/>
</svg>
<span class="circuit-label top">01 / GENERATE</span><span class="circuit-label right">02 / VALIDATE</span>
<span class="circuit-label bottom">03 / REPORT</span>
<div class="circuit-center" aria-hidden="true"><strong>K.</strong></div>
</div>
<div class="board-stats"><div class="board-kicker">DEPLOYED SITE / BUILD-TIME REPORT</div>
<div class="board-stat-grid"><div><strong data-audit-pages>…</strong><span>Pages checked</span></div>
<div><strong data-audit-errors>…</strong><span>Errors reported</span></div></div>
<p class="board-status" data-audit-status role="status">Reading the published audit…</p>
<p class="board-status" data-audit-footnote></p>
<a class="board-link" href="{base}/seo-health.html">Inspect full report ↗</a></div></aside>"""

    home = f"""
<section class="hero multi-hero" aria-label="Introduction to Kestrel">
<div class="hero-copy" data-reveal>
{kicker("FIELD NOTE 001 / OPEN SOURCE SEO ENGINEERING")}
<h1>Good SEO needs <em>good systems.</em></h1>
<p class="hero-lede">Kestrel is a working demonstration of the less glamorous work behind organic growth. Structured publishing. Technical quality checks. Clear evidence when something goes wrong.</p>
<div class="hero-actions"><a class="cta" href="{link('/lab/')}">Explore the diagnostic lab ↗</a><a class="cta-outline" href="{link('/systems/')}">See how it works</a></div>
<p class="hero-footnote">The programme data is fictional. The Python automation, tests, workflows and audit outputs are inspectable.</p>
</div>{board}</section>
<div class="ticker" aria-label="Technical SEO operations">
<span class="ticker-label">KESTREL SYSTEMS</span><div class="ticker-track" aria-hidden="true">
<span>Generate pages</span><span>Validate HTML</span><span>Monitor releases</span><span>Extract Google data</span>
<span>Generate pages</span><span>Validate HTML</span></div></div>
<section class="section" data-reveal>
<div class="section-heading"><div>{kicker("01 / EXPLORE THE SITE")}
<h2>An actual website.<br><em>Separate working parts.</em></h2></div>
<p>Go deeper into the technical architecture, try educational failure scenarios, or inspect the generated programme pages and source code.</p></div>
<div class="route-grid">
{section_card("01 / ARCHITECTURE","The systems","How the release gate, monitoring and Google API integrations fit together.","/systems/","Python · GitHub Actions · APIs")}
{section_card("02 / EXPERIMENT","The diagnostic lab","Explore an interactive demonstration of three common technical SEO failures.","/lab/","Interactive, simulated examples")}
{section_card("03 / DATASET","The page library","Browse structured programme data rendered into real, separate HTML files.","/programmes/","{record_count} fictional records · {market_count} markets")}
{section_card("04 / ENGINEERING STORY","The case study","See the problem, design decisions, implementation evidence and limitations.","/case-studies/kestrel/","Code and reproducible checks")}
</div></section>
<section class="proof-band" data-reveal>
<div><span class="overline">THE APPROACH</span><h2>Evidence<br>before confidence.</h2></div>
<div><p>Every claim about the build can be traced to code, tests or an audit output. Sample performance data and hypothetical SEO incidents are labeled as such.</p>
<a class="cta-outline" href="{link('/about/')}">Why this project exists ↗</a></div>
</section>
"""
    systems = f"""{breadcrumb([("Systems", "/systems/")])}
<header class="page-masthead" data-reveal>{kicker("01 / ARCHITECTURE")}
<h1>Systems that <em>do the checking.</em></h1>
<p>Every technical SEO risk has a process behind it: a source, a rule, a result and someone responsible for the next action. This section documents Kestrel's actual implementation and optional integrations.</p></header>
<div class="route-grid route-grid-three">
{section_card("01 / PRE-RELEASE","Release gate","Validation before deployment: source records, metadata, canonical rules, internal links and structured data.","/systems/release-gate/","Implemented · tested")}
{section_card("02 / POST-RELEASE","Live monitoring","A bounded, robots-aware crawler that produces an audit report for human follow-up.","/systems/live-monitoring/","Implemented · scheduled workflow")}
{section_card("03 / REPORTING","Google APIs","How the Google Search Console and GA4 read-only APIs fit into the reporting pipeline.","/systems/google-apis/","Code available · authorization required")}
</div>
<section class="content-slab" data-reveal>{kicker("HOW THE PIECES CONNECT")}
<h2>From a CSV to a reviewable release.</h2>
<div class="pipeline-steps">
<div><span>01</span><strong>Source records</strong><small>CSV data and publication states</small></div>
<div><span>02</span><strong>Build</strong><small>Python templates → HTML pages</small></div>
<div><span>03</span><strong>Validate</strong><small>Tests and QA rules in CI</small></div>
<div><span>04</span><strong>Deploy</strong><small>GitHub Pages after checks pass</small></div>
<div><span>05</span><strong>Monitor</strong><small>Audit reports and reviewed findings</small></div>
</div>
<p class="micro-note">The monitoring and Google API components have different deployment and authorization requirements. See each system page for what is verified and what remains optional.</p>
<a class="text-arrow" href="{repo}/actions">Review workflow runs ↗</a>
</section>
"""

    release = f"""{breadcrumb([("Systems","/systems/"),("Release gate","/systems/release-gate/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 01 / PRE-PUBLICATION")}
<h1>Catch it before <em>it ships.</em></h1>
<p>Kestrel treats technical SEO quality as part of the website build. Known violations can fail a release rather than quietly reach production.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>What gets checked?</h2>
<p>The generator begins with a structured CSV. A first validation pass checks publication status, required fields, market-currency rules, duplication and stale source indicators. Invalid source records stop the build.</p>
<div class="checks-list">
<div><b>01 / CONTENT DATA</b><span>Required fields, status, duplicate programme-market keys</span></div>
<div><b>02 / GENERATED HTML</b><span>Titles, descriptions, H1s, internal navigation, canonicals</span></div>
<div><b>03 / STRUCTURED DATA</b><span>JSON-LD syntax and selected schema requirements</span></div>
<div><b>04 / MIGRATION RULES</b><span>Redirect cycles, chains and self-redirects</span></div>
</div>
<h2>How it blocks a release</h2>
<pre class="code-example"><code>python pseo_checker.py data/pages.csv
python build.py --base-url "$BASE"
python qa.py dist
python -m seo_ops.cli audit-dir dist --strict</code></pre>
<p>GitHub Actions runs these steps and exits with a failure status if a blocking check fails. The publish job depends on the successful build job.</p>
<h2>What it still needs from a person</h2>
<p>A passing rule check cannot prove the truth of a programme's fees or that a page satisfies search intent. Those judgments require validated sources and human review.</p>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">INSPECT THE EVIDENCE</span>
<h3>Read the source.</h3>
<p>This is verifiable repository code rather than a narrated mockup.</p>
<a class="text-arrow" href="{repo}/blob/main/build.py">Page generator ↗</a>
<a class="text-arrow" href="{repo}/blob/main/qa.py">HTML QA checks ↗</a>
<a class="text-arrow" href="{repo}/actions">GitHub Actions runs ↗</a>
</aside></div>"""

    monitoring = f"""{breadcrumb([("Systems","/systems/"),("Live monitoring","/systems/live-monitoring/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 02 / POST-PUBLICATION")}
<h1>The deploy is <em>the beginning.</em></h1>
<p>Automated monitoring makes it easier to spot issues that appear after publication, while preserving a clear record of the affected pages and check results.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>What the crawler does</h2>
<p>The Python crawler starts from an approved URL, stays within the configured site scope, respects robots rules, limits the number of pages and waits between requests. It collects response and HTML signals for an audit.</p>
<div class="checks-list">
<div><b>HTTP RESPONSES</b><span>Unexpected errors and redirects</span></div>
<div><b>INDEXABILITY</b><span>HTML robots directives against an explicitly expected state</span></div>
<div><b>CONTENT STRUCTURE</b><span>Titles, headings and canonical references</span></div>
<div><b>SCHEMA</b><span>JSON-LD validation when required by the page specification</span></div>
</div>
<h2>The monitoring workflow</h2>
<pre class="code-example"><code>python -m seo_ops.cli crawl \
  --url "https://example.org/" \
  --max-pages 30 --delay 0.4 \
  --out reports/live-audit.json \
  --html reports/live-audit.html</code></pre>
<p>GitHub Actions contains a scheduled monitoring job. Report artifacts can be inspected after a run; optional webhooks require a configured destination.</p>
<h2>Boundaries that matter</h2>
<p>This crawler doesn't execute client-side JavaScript, infer actual Google rankings or guarantee a 24-hour incident response. A larger production deployment would need coverage rules, alert delivery, retries and monitoring of the monitor.</p>
<a class="cta" href="{link('/lab/')}">Explore example failures ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">CODE AND OUTPUTS</span>
<h3>Audit, then investigate.</h3>
<a class="text-arrow" href="{base}/seo-health.html">Published build-time audit ↗</a>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/crawler.py">Crawler source ↗</a>
<a class="text-arrow" href="{repo}/blob/main/.github/workflows/seo-ops-monitor.yml">Monitoring configuration ↗</a>
</aside></div>"""

    apis = f"""{breadcrumb([("Systems","/systems/"),("Google APIs","/systems/google-apis/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 03 / PERFORMANCE DATA")}
<h1>Follow the data. <em>Keep it honest.</em></h1>
<p>Technical SEO work becomes more useful when it connects to search visibility and meaningful website behavior. Kestrel contains optional, read-only Google API integrations designed for that purpose.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>Two sources, different questions.</h2>
<div class="checks-list">
<div><b>SEARCH CONSOLE API</b><span>Page-level impressions, clicks, CTR and average position</span></div>
<div><b>GOOGLE ANALYTICS 4 API</b><span>Daily website sessions and configured key events</span></div>
</div>
<p>Analytics and Search Console data have different definitions and collection limitations. Their reported numbers should be reconciled carefully rather than treated as interchangeable.</p>
<h2>What is implemented?</h2>
<p>The repository contains Python routines that can authenticate with authorized Google credentials, request data from the respective APIs and produce CSV exports. Account access and real property identifiers still need to be configured.</p>
<pre class="code-example"><code>python -m seo_ops.cli google-pull \
  --gsc-property "https://example.org/" \
  --ga4-property "123456789" \
  --output-dir reports</code></pre>
<h2>What about the fictional website?</h2>
<p>Kestrel programme pages remain noindex. A verified Search Console property may have little or no organic-search data, especially on a new demonstration website. Empty responses should be shown as empty. Synthetic fixtures are kept separate for teaching and testing.</p>
<a class="cta" href="{repo}/blob/main/docs/GOOGLE_SETUP.md">Read the integration guide ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">API REFERENCES</span>
<h3>Trace the request.</h3>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/google_data.py">Read API connector code ↗</a>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/examples/gsc-synthetic.csv">Synthetic GSC test data ↗</a>
<a class="text-arrow" href="{repo}/blob/main/docs/GOOGLE_SETUP.md">Authorization setup ↗</a>
</aside></div>"""

    scenario = f"""{breadcrumb([("Diagnostic lab","/lab/")])}
<header class="page-masthead" data-reveal>{kicker("02 / INTERACTIVE LAB")}
<h1>Break something. <em>Find the cause.</em></h1>
<p>Choose a hypothetical SEO problem, inspect the relevant code and see what an automated checker should flag. The examples are educational simulations. The audit panel below reads actual output from Kestrel's build.</p></header>
<section class="experiment standalone-lab" id="laboratory" aria-label="Interactive example technical SEO diagnostics" data-reveal>
<div class="eyebrow section-index">PREDEFINED EXAMPLES / SIMULATED FAILURES</div>
<h2>What would <em>you catch?</em></h2>
<p class="experiment-lede">Use the tabs to compare indexability, canonical and internal-link problems.</p>
<div class="lab-shell">
<div class="scenario-controls" role="tablist" aria-label="Choose a sample SEO failure">
<h3>CHOOSE THE SCENARIO</h3>
<button type="button" role="tab" class="scenario-tab" data-scenario="noindex" aria-selected="true" aria-controls="scenario-panel">01 / Accidental noindex</button>
<button type="button" role="tab" class="scenario-tab" data-scenario="canonical" aria-selected="false" aria-controls="scenario-panel" tabindex="-1">02 / Wrong canonical</button>
<button type="button" role="tab" class="scenario-tab" data-scenario="link" aria-selected="false" aria-controls="scenario-panel" tabindex="-1">03 / Broken internal link</button>
</div>
<div class="scenario-output" id="scenario-panel" role="tabpanel" aria-live="polite">
<span class="scenario-location" data-scenario-path>/programmes/online-mba-ghana/</span>
<pre class="scenario-code"><code data-scenario-code>&lt;meta name="robots" content="noindex"&gt;</code></pre>
<div class="scenario-finding"><strong data-scenario-level>CRITICAL · INDEXABILITY</strong>
<h3 data-scenario-title>An important page is excluded</h3>
<p data-scenario-explanation>Compare the page's actual directive with an approved indexability baseline.</p></div>
</div></div>
<p class="lab-caption">SIMULATION ONLY · Tab selections change example data. They do not crawl a website or create live incidents.</p>
</section>
<section class="two-part-section" data-reveal>
<div><div class="eyebrow section-index">REAL OUTPUT</div>
<h2>What did the actual build report?</h2>
<p>The status board below reads the published JSON audit. The site is fictional, but the HTML checks are executed as part of its deployment process.</p>
<a class="text-arrow" href="{base}/seo-health.html">Open the full audit ↗</a></div>
{board}
</section>"""

    case = f"""{breadcrumb([("Case studies","/case-studies/kestrel/"),("Kestrel","/case-studies/kestrel/")])}
<header class="page-masthead" data-reveal>{kicker("03 / PROJECT STUDY")}
<h1>A website that <em>checks itself.</em></h1>
<p>Kestrel is an intentionally fictional eCampus and a reproducible engineering exercise. Its purpose is to show how structured content, automated SEO validation and human decisions can work together.</p></header>
<section class="case-intro" data-reveal>
<div class="case-number"><span>PROJECT / 001</span><strong>{record_count}</strong><span>FICTIONAL CONTENT RECORDS</span></div>
<div><h2>The problem it explores</h2><p>As sites expand, publishing dozens or hundreds of URLs can multiply simple technical mistakes. Manual review may miss duplicate metadata, unexpected directives, broken paths or incomplete schema.</p><p>Kestrel demonstrates a small release pipeline with documented checks and a readable report. It is a portfolio prototype, without claims of organic acquisition results or client deployment.</p></div>
</section>
<section class="section" data-reveal>
<div class="section-heading"><div>{kicker("THE ENGINEERING DECISIONS")}<h2>Built in layers.</h2></div>
<p>Each step handles a different class of failure and leaves evidence for an engineer or SEO specialist to inspect.</p></div>
<div class="workflow-grid">
<article class="workflow-step"><span class="step-no">01 / CONTENT</span><h3>Structured inputs.</h3><p>Each programme-country combination begins as a validated CSV record, with hold/publish states.</p></article>
<article class="workflow-step"><span class="step-no">02 / QUALITY</span><h3>Release checks.</h3><p>Python inspects the generated HTML and reports blocking issues during CI.</p></article>
<article class="workflow-step"><span class="step-no">03 / OPERATIONS</span><h3>Readable evidence.</h3><p>JSON and HTML reports make findings usable for machines and for people.</p></article>
</div></section>
<section class="proof-band" data-reveal>
<div><span class="overline">SEE THE WORK</span><h2>Inspect the actual implementation.</h2></div>
<div><p>Source code, unit tests, generated pages and GitHub Actions logs are public. The test data is expressly fictional and remains noindex.</p>
<a class="cta" href="{repo}">Open GitHub repository ↗</a>
<a class="text-arrow" href="{repo}/actions">Review release history ↗</a></div>
</section>"""

    about = f"""{breadcrumb([("About","/about/")])}
<header class="page-masthead" data-reveal>{kicker("THE PURPOSE OF THIS LAB")}
<h1>Curiosity, <em>with controls.</em></h1>
<p>Kestrel was created as a hands-on portfolio environment for technical SEO, programmatic publishing, measurement and workflow automation.</p></header>
<section class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>Why build a fictional website?</h2>
<p>Real websites have brand, customer and operational constraints. A clearly fictional site provides a safe place to introduce technical SEO mistakes, test automated rules and share a complete implementation without exposing confidential data.</p>
<h2>Built around repeatable decisions</h2>
<p>Good automation should explain its own inputs and outputs. Kestrel keeps page data separate from templates, tests the generated HTML, records findings and makes human review a visible part of the process.</p>
<h2>Who created it?</h2>
<p>This independent demonstration was built by Grace Odukoya, a specialist working across technical SEO, growth measurement, content systems and business automation.</p>
<p>The visual system uses a restrained editorial interpretation of Prism Authority's established colour identity.</p>
<a class="cta" href="{link('/case-studies/kestrel/')}">Read the project case study ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">DESIGN SYSTEM</span>
<h3>Prism Authority / applied.</h3>
<p>Imperial Iris, Deep Teal, Amber, Porcelain and Night Ink. Strong contrast, editorial typography and motion that helps explain the technical story.</p>
<div class="brand-swatches" aria-label="Prism Authority colours">
<span style="background:#533E80" title="Imperial Iris"></span>
<span style="background:#166D73" title="Deep Teal"></span>
<span style="background:#E9AC4E" title="Amber"></span>
<span style="background:#F8F6F1" title="Porcelain"></span>
<span style="background:#171923" title="Night Ink"></span>
</div>
<a class="text-arrow" href="{repo}/blob/main/docs/INTERACTIVE_SITE.md">Interface documentation ↗</a>
</aside></section>"""

    return {
        "/": page("/", "Kestrel | Interactive SEO engineering lab", "Explore Kestrel's interactive technical SEO systems, live quality-control reports and fictional programmatic page library.", home),
        "/about/": page("/about/", "About the Kestrel SEO Operations Lab", "Meet the independently built technical SEO and automation demonstration, its purpose, controls and engineering philosophy.", about),
        "/systems/": page("/systems/", "SEO automation systems | Kestrel", "Explore Kestrel's release gate, technical crawler, and read-only Google Analytics and Search Console integrations.", systems),
        "/systems/release-gate/": page("/systems/release-gate/", "Automated SEO release gate | Kestrel", "See how Python tests, metadata checks and GitHub Actions detect technical SEO problems before a website release.", release),
        "/systems/live-monitoring/": page("/systems/live-monitoring/", "Technical SEO monitoring | Kestrel", "Learn how the Kestrel crawler checks live pages and creates readable technical SEO issue reports.", monitoring),
        "/systems/google-apis/": page("/systems/google-apis/", "GA4 and GSC API automation | Kestrel", "Understand the read-only GA4 and Google Search Console API connectors, credentials and reporting checks in Kestrel.", apis),
        "/lab/": page("/lab/", "Interactive technical SEO diagnostic lab | Kestrel", "Try simulated noindex, canonical and broken-link scenarios alongside Kestrel's actual published SEO audit.", scenario),
        "/case-studies/kestrel/": page("/case-studies/kestrel/", "Kestrel technical SEO engineering case study", "Discover the architecture, validation and reporting design behind Kestrel's reproducible programmatic SEO project.", case),
    }
