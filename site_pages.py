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
<p class="hero-lede">Kestrel shows how to build web pages, check them for SEO mistakes, and spot problems early. You can explore the tools and see how they work.</p>
<div class="hero-actions"><a class="cta" href="{link('/lab/')}">Explore the diagnostic lab ↗</a><a class="cta-outline" href="{link('/systems/')}">See how it works</a></div>
<p class="hero-footnote">The courses are made up for this demo. You can see the real code, tests, and reports.</p>
</div>{board}</section>
<div class="ticker" aria-label="Technical SEO operations">
<span class="ticker-label">KESTREL SYSTEMS</span><div class="ticker-track" aria-hidden="true">
<span>Generate pages</span><span>Validate HTML</span><span>Monitor releases</span><span>Extract Google data</span>
<span>Generate pages</span><span>Validate HTML</span></div></div>
<section class="section" data-reveal>
<div class="section-heading"><div>{kicker("01 / EXPLORE THE SITE")}
<h2>One website.<br><em>Many useful tools.</em></h2></div>
<p>See how the tools work, try a sample SEO problem, or explore the pages built with Python.</p></div>
<div class="route-grid">
{section_card("01 / ARCHITECTURE","The systems","See how Kestrel checks pages before and after they go live.","/systems/","Python · Site checks · GitHub")}
{section_card("02 / EXPERIMENT","The diagnostic lab","Try three common SEO mistakes and learn how to spot them.","/lab/","Hands-on examples")}
{section_card("03 / DATASET","The page library","Explore sample course pages built from one set of data.","/programmes/","{record_count} sample courses · {market_count} countries")}
{section_card("04 / ENGINEERING STORY","The case study","Learn why Kestrel was made, what works, and what still needs work.","/case-studies/kestrel/","Real code and test results")}
</div></section>
<section class="proof-band" data-reveal>
<div><span class="overline">THE APPROACH</span><h2>Check the work.<br>Trust the facts.</h2></div>
<div><p>You can check the code, tests, and reports yourself. Sample data and made-up SEO problems are marked clearly.</p>
<a class="cta-outline" href="{link('/about/')}">Why I built Kestrel ↗</a></div>
</section>
"""
    systems = f"""{breadcrumb([("Systems", "/systems/")])}
<header class="page-masthead" data-reveal>{kicker("01 / ARCHITECTURE")}
<h1>Systems that <em>do the checking.</em></h1>
<p>A good SEO check needs clear steps. Where does the data come from? What needs checking? What happens when something fails? Explore each part here.</p></header>
<div class="route-grid route-grid-three">
{section_card("01 / PRE-RELEASE","Release gate","Check page data, links, and SEO tags before publishing.","/systems/release-gate/","Built and tested")}
{section_card("02 / POST-RELEASE","Live monitoring","A tool that visits pages, checks for problems, and writes a report.","/systems/live-monitoring/","Built · Scheduled check")}
{section_card("03 / REPORTING","Google APIs","See how GA4 and Google Search Console can send data to a report.","/systems/google-apis/","Code ready · Google access needed")}
</div>
<section class="content-slab" data-reveal>{kicker("HOW THE PIECES CONNECT")}
<h2>From a spreadsheet to a checked website.</h2>
<div class="pipeline-steps">
<div><span>01</span><strong>Source records</strong><small>Course details and page status</small></div>
<div><span>02</span><strong>Build</strong><small>Python creates web pages</small></div>
<div><span>03</span><strong>Validate</strong><small>Code checks for mistakes</small></div>
<div><span>04</span><strong>Deploy</strong><small>Website goes live if tests pass</small></div>
<div><span>05</span><strong>Monitor</strong><small>Reports show what needs fixing</small></div>
</div>
<p class="micro-note">Some tools need extra setup or Google account access. Each page shows what works now and what still needs setting up.</p>
<a class="text-arrow" href="{repo}/actions">See the test history ↗</a>
</section>
"""

    release = f"""{breadcrumb([("Systems","/systems/"),("Release gate","/systems/release-gate/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 01 / PRE-PUBLICATION")}
<h1>Catch it before <em>it ships.</em></h1>
<p>Kestrel checks each page before it goes live. If a serious SEO check fails, the new site version does not get published.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>What gets checked?</h2>
<p>Each course starts as a row in a CSV file, like a spreadsheet. Kestrel checks that key details are filled in, the course is ready to publish, and there are no duplicate records. If a key check fails, the build stops.</p>
<div class="checks-list">
<div><b>01 / CONTENT DATA</b><span>Missing details, page status, duplicate courses</span></div>
<div><b>02 / GENERATED HTML</b><span>Page titles, descriptions, headings, links, and preferred URLs</span></div>
<div><b>03 / STRUCTURED DATA</b><span>Checks code that helps search engines understand a page</span></div>
<div><b>04 / MIGRATION RULES</b><span>Links that send visitors around in circles or through too many steps</span></div>
</div>
<h2>How it blocks a release</h2>
<pre class="code-example"><code>python pseo_checker.py data/pages.csv
python build.py --base-url "$BASE"
python qa.py dist
python -m seo_ops.cli audit-dir dist --strict</code></pre>
<p>GitHub runs these tests for us. If an important check fails, the site does not publish that change.</p>
<h2>What it still needs from a person</h2>
<p>A passing test cannot prove that a course fee is correct or that the page answers what readers need. A person still needs to check those things.</p>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">INSPECT THE EVIDENCE</span>
<h3>Read the source.</h3>
<p>These links lead to real code and test results.</p>
<a class="text-arrow" href="{repo}/blob/main/build.py">Page generator ↗</a>
<a class="text-arrow" href="{repo}/blob/main/qa.py">HTML QA checks ↗</a>
<a class="text-arrow" href="{repo}/actions">GitHub Actions runs ↗</a>
</aside></div>"""

    monitoring = f"""{breadcrumb([("Systems","/systems/"),("Live monitoring","/systems/live-monitoring/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 02 / POST-PUBLICATION")}
<h1>The deploy is <em>the beginning.</em></h1>
<p>SEO problems can appear after a page goes live. Kestrel can check pages again and save what it finds.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>What the crawler does</h2>
<p>The Python crawler starts with a website link. It stays on that site, follows its crawl rules, and checks a set number of pages. It then saves the results.</p>
<div class="checks-list">
<div><b>HTTP RESPONSES</b><span>Pages that fail to load or point somewhere else</span></div>
<div><b>INDEXABILITY</b><span>Tags that tell Google whether to show a page</span></div>
<div><b>CONTENT STRUCTURE</b><span>Page titles, headings, and preferred URLs</span></div>
<div><b>SCHEMA</b><span>Checks the page's structured data code</span></div>
</div>
<h2>The monitoring workflow</h2>
<pre class="code-example"><code>python -m seo_ops.cli crawl \
  --url "https://example.org/" \
  --max-pages 30 --delay 0.4 \
  --out reports/live-audit.json \
  --html reports/live-audit.html</code></pre>
<p>GitHub can run the page checker on a schedule. You can read its report after each run. Sending alerts to another app needs extra setup.</p>
<h2>Boundaries that matter</h2>
<p>The crawler cannot see every page built with JavaScript. It also cannot tell you where Google ranks a page. For a real business, we would add stronger alerts and checks for failed runs.</p>
<a class="cta" href="{link('/lab/')}">Try the sample issues ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">CODE AND OUTPUTS</span>
<h3>Check. Find. Fix.</h3>
<a class="text-arrow" href="{base}/seo-health.html">See the latest site report ↗</a>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/crawler.py">Crawler source ↗</a>
<a class="text-arrow" href="{repo}/blob/main/.github/workflows/seo-ops-monitor.yml">Monitoring configuration ↗</a>
</aside></div>"""

    apis = f"""{breadcrumb([("Systems","/systems/"),("Google APIs","/systems/google-apis/")])}
<header class="page-masthead" data-reveal>{kicker("SYSTEM 03 / PERFORMANCE DATA")}
<h1>Follow the data. <em>Keep it honest.</em></h1>
<p>SEO reports are more useful when they show both Google Search results and what visitors do on your site. Kestrel has code to read that data, once Google access is set up.</p></header>
<div class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>Two sources, different questions.</h2>
<div class="checks-list">
<div><b>SEARCH CONSOLE API</b><span>Page-level impressions, clicks, CTR and average position</span></div>
<div><b>GOOGLE ANALYTICS 4 API</b><span>Daily website sessions and configured key events</span></div>
</div>
<p>GA4 and Search Console count different things. Their numbers may not match. We need to check what each number means before using it.</p>
<h2>What is implemented?</h2>
<p>Kestrel has Python code that can ask Google for data and save it in CSV files. We still need to connect an approved Google account and the right property IDs.</p>
<pre class="code-example"><code>python -m seo_ops.cli google-pull \
  --gsc-property "https://example.org/" \
  --ga4-property "123456789" \
  --output-dir reports</code></pre>
<h2>What about the fictional website?</h2>
<p>Kestrel's sample course pages are set to stay out of Google search. That means Search Console may show little or no traffic. We'll show empty results as they are and mark any practice data as fake.</p>
<a class="cta" href="{repo}/blob/main/docs/GOOGLE_SETUP.md">Read the integration guide ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">API REFERENCES</span>
<h3>See the code.</h3>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/google_data.py">Read API connector code ↗</a>
<a class="text-arrow" href="{repo}/blob/main/seo_ops/examples/gsc-synthetic.csv">Synthetic GSC test data ↗</a>
<a class="text-arrow" href="{repo}/blob/main/docs/GOOGLE_SETUP.md">Authorization setup ↗</a>
</aside></div>"""

    scenario = f"""{breadcrumb([("Diagnostic lab","/lab/")])}
<header class="page-masthead" data-reveal>{kicker("02 / INTERACTIVE LAB")}
<h1>Break something. <em>Find the cause.</em></h1>
<p>Choose a sample SEO mistake and see why it matters. These examples are made up for learning. The report below shows the results from Kestrel's real build tests.</p></header>
<section class="experiment standalone-lab" id="laboratory" aria-label="Interactive example technical SEO diagnostics" data-reveal>
<div class="eyebrow section-index">PREDEFINED EXAMPLES / SIMULATED FAILURES</div>
<h2>What would <em>you catch?</em></h2>
<p class="experiment-lede">Choose a problem to see what went wrong and what to check next.</p>
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
<p class="lab-caption">SAMPLE PROBLEMS ONLY · These buttons show practice examples. They do not run a live scan.</p>
</section>
<section class="two-part-section" data-reveal>
<div><div class="eyebrow section-index">REAL OUTPUT</div>
<h2>What did the actual build report?</h2>
<p>The board below reads the real test report from the published site. The course details are made up, but the code checks really run.</p>
<a class="text-arrow" href="{base}/seo-health.html">Read the full report ↗</a></div>
{board}
</section>"""

    case = f"""{breadcrumb([("Case studies","/case-studies/kestrel/"),("Kestrel","/case-studies/kestrel/")])}
<header class="page-masthead" data-reveal>{kicker("03 / PROJECT STUDY")}
<h1>A website that <em>checks itself.</em></h1>
<p>Kestrel is a made-up school website used to practise real SEO skills. It shows how Python can create pages, check them for mistakes, and help people review the results.</p></header>
<section class="case-intro" data-reveal>
<div class="case-number"><span>PROJECT / 001</span><strong>{record_count}</strong><span>FICTIONAL CONTENT RECORDS</span></div>
<div><h2>The problem it explores</h2><p>When a website has hundreds of pages, small SEO mistakes can spread fast. Some pages may have the wrong title, missing links, or tags that keep them out of search.</p><p>Kestrel runs checks before a site update goes live and writes a report you can read. It's a practice project. It has no real customer results to claim.</p></div>
</section>
<section class="section" data-reveal>
<div class="section-heading"><div>{kicker("THE ENGINEERING DECISIONS")}<h2>Built in layers.</h2></div>
<p>Each step checks a different problem and saves the result.</p></div>
<div class="workflow-grid">
<article class="workflow-step"><span class="step-no">01 / CONTENT</span><h3>Structured inputs.</h3><p>Each course and country starts as one row in a CSV file. A row can be ready or on hold.</p></article>
<article class="workflow-step"><span class="step-no">02 / QUALITY</span><h3>Release checks.</h3><p>Python checks the web pages. Serious errors stop the build.</p></article>
<article class="workflow-step"><span class="step-no">03 / OPERATIONS</span><h3>Readable evidence.</h3><p>The reports show the results in formats people and software can read.</p></article>
</div></section>
<section class="proof-band" data-reveal>
<div><span class="overline">SEE THE WORK</span><h2>Inspect the actual implementation.</h2></div>
<div><p>You can open the code, page tests, and GitHub logs. The course details are fake and kept out of search.</p>
<a class="cta" href="{repo}">Open GitHub repository ↗</a>
<a class="text-arrow" href="{repo}/actions">Review release history ↗</a></div>
</section>"""

    about = f"""{breadcrumb([("About","/about/")])}
<header class="page-masthead" data-reveal>{kicker("THE PURPOSE OF THIS LAB")}
<h1>Curiosity, <em>with controls.</em></h1>
<p>I built Kestrel to practise SEO, coding, data tracking, and automation with a website I can test safely.</p></header>
<section class="editorial-columns">
<article class="editorial-main" data-reveal>
<h2>Why build a fictional website?</h2>
<p>Real businesses have people and data to protect. A made-up school lets me test SEO problems and show my work without sharing private client details.</p>
<h2>Built around repeatable decisions</h2>
<p>A good automation should show what went in, what happened, and what came out. Kestrel keeps course data separate, checks each page, and saves the results for review.</p>
<h2>Who created it?</h2>
<p>I built this project to show how my SEO, analytics, content, and automation skills work together.</p>
<p>The site uses the Prism Authority colours with clean type, strong contrast, and clear layouts.</p>
<a class="cta" href="{link('/case-studies/kestrel/')}">Read the project case study ↗</a>
</article>
<aside class="editorial-sidebar" data-reveal><span class="eyebrow">DESIGN SYSTEM</span>
<h3>Prism Authority / applied.</h3>
<p>Iris, Teal, Amber, Porcelain, and Night Ink. Clear text, simple motion, and enough space to read.</p>
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
        "/about/": page("/about/", "About the Kestrel SEO Operations Lab", "Learn why I made Kestrel, how it works, and how I test it.", about),
        "/systems/": page("/systems/", "SEO automation systems | Kestrel", "Explore Kestrel's release gate, technical crawler, and read-only Google Analytics and Search Console integrations.", systems),
        "/systems/release-gate/": page("/systems/release-gate/", "Automated SEO release gate | Kestrel", "See how Python tests, metadata checks and GitHub Actions detect technical SEO problems before a website release.", release),
        "/systems/live-monitoring/": page("/systems/live-monitoring/", "Technical SEO monitoring | Kestrel", "Learn how the Kestrel crawler checks live pages and creates readable technical SEO issue reports.", monitoring),
        "/systems/google-apis/": page("/systems/google-apis/", "GA4 and GSC API automation | Kestrel", "Understand the read-only GA4 and Google Search Console API connectors, credentials and reporting checks in Kestrel.", apis),
        "/lab/": page("/lab/", "Interactive technical SEO diagnostic lab | Kestrel", "Try sample SEO problems and read a real report from Kestrel's page checks.", scenario),
        "/case-studies/kestrel/": page("/case-studies/kestrel/", "Kestrel technical SEO engineering case study", "Discover the architecture, validation and reporting design behind Kestrel's reproducible programmatic SEO project.", case),
    }
