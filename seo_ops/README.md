# SEO Operations Control Center

**Automated technical SEO checks, release QA, site monitoring and data-led content workflows**

**Built by Grace Odukoya** | SEO specialist & automation builder  
**Stack:** Python, JSON-LD, Google Search Console API, GA4 Data API, Google Apps Script, Google Sheets, GitHub Actions

[View the complete repository](../README.md) · [Read the implementation case study](docs/PORTFOLIO_CASE_STUDY.md) · [See the deployment workflow](../.github/workflows/deploy.yml)

## The idea

When a team publishes or updates dozens of pages, technical SEO becomes an operational challenge. A missing canonical tag, malformed schema markup, accidental noindex directive or faulty redirect map can affect many URLs.

I built this SEO Operations Control Center to turn repeatable checks into an **automated system with clear reports and human decision points**. The aim is straightforward: **spot technical risks earlier, reduce routine manual checking, and help SEO and content teams focus on fixes and growth opportunities.**

This implementation runs against Kestrel eCampus, a fictional programmatic SEO website. It is designed as an open, reproducible example that recruiters, founders and SEO developers can inspect and run.

## What it delivers

| Workflow | Why a business would care | How it works technically | Where to look |
| --- | --- | --- | --- |
| **SEO release gate** | Catch preventable issues before new pages go live | Audits built HTML during GitHub Actions CI; a failed check can stop deployment | [Deployment workflow](../.github/workflows/deploy.yml), [core.py](core.py) |
| **Schema validation** | Find broken structured data before search engines process the page | Parses JSON-LD, reads graph structures and checks essential fields for supported schema types | [core.py](core.py), [tests](tests/) |
| **Technical crawl monitor** | Surface errors without relying on someone to manually check URLs | Bounded, robots-aware crawl checks HTTP responses, titles, canonicals, H1s and noindex signals | [crawler.py](crawler.py), [scheduled Action](../.github/workflows/seo-ops-monitor.yml) |
| **Redirect-map QA** | Reduce avoidable migration mistakes | Reviews a source/destination CSV for duplicate redirects, self-redirects, chains and cycles | [redirect checker](core.py), [sample mapping](redirects.csv) |
| **SEO health reporting** | Make issues understandable to technical and nontechnical stakeholders | Produces an HTML report for people and JSON for downstream automation | [reporting.py](reporting.py) |
| **Google Search Console + GA4 extracts** | Bring search and conversion performance into a repeatable reporting workflow | Read-only official API requests, using Google account permissions | [google_data.py](google_data.py) |
| **Content-refresh queue** | Help editors decide which existing pages deserve attention | Ranks page-level GSC opportunities, with an explicit human approval status | [refresh.py](refresh.py) |
| **Google Sheets + email alerts** | Make SEO issues visible to people outside GitHub | Apps Script syncs a published report into Sheets and emails newly detected error sets | [Code.gs](apps_script/Code.gs) |
| **A/B test planning** | Set decision rules before changing high-value pages | Estimates sample size per variant and evaluates fixed-horizon conversion outcomes | [experiments.py](experiments.py) |

### What is running, and what needs connection?

**Implemented and verified:** local HTML checks, JSON-LD validation, redirect-map review, reports, automated unit tests and CI release checks. The repository's deployment workflow has completed successfully with these checks.

**Available to configure:** read-only GSC/GA4 extraction, Apps Script → Google Sheets synchronization, alert webhooks and destination-specific live monitoring. These require access to real accounts, websites or notification endpoints. The weekly crawl workflow is committed and can be run through GitHub Actions.

## How the system works

~~~text
CONTENT & RELEASE
CSV content → data validation → generated pages → HTML + JSON-LD audit
                                                |
                                     issues found? → block release
                                                |
                                         checks pass
                                                |
                                        deploy website

POST-LAUNCH MONITORING
Scheduled crawl → technical SEO findings → JSON + readable HTML
                                             |
                             optional webhook / Apps Script → Sheets + alerts

GROWTH OPERATIONS
GSC page data → priority scoring → human-reviewed refresh queue
GA4 data      → daily session and key-event export
A/B test plan → sample-size target → experiment assessment
~~~

The separation is intentional. **A release check catches issues before publication. A live monitor checks what visitors can actually access. Performance data supports prioritization, while publication decisions remain with people.**

## Reproduce the project

### 1. Install and test

Requires **Python 3.10+**. Core checks use the standard library, so no paid service or package installation is needed.

From the repository root:

~~~bash
git clone https://github.com/graceomolola001-cmyk/kestrel-pseo.git
cd kestrel-pseo

python -m unittest discover -s seo_ops/tests -v
~~~

The included test suite covers valid and invalid schema, JSON-LD graph context, duplicate and cyclic redirects, local auditing, editorial review status and conversion-test sample-size logic.

### 2. Build the sample pages and run pre-publish QA

~~~bash
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python qa.py dist

python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out reports/prepublish.json --html reports/prepublish.html --strict
python -m seo_ops.cli redirects seo_ops/redirects.csv --strict
~~~

**Review the output:** Open **reports/prepublish.html** for a human-readable SEO health report. The companion JSON report contains severity, check code, affected URL and explanation.

**What --strict does:** Returns a failing exit status when the audit finds an error, so CI can stop a problematic release. Warnings remain visible for review.

### 3. Run an on-site SEO crawl

Use a domain you own or have permission to audit:

~~~bash
python -m seo_ops.cli crawl --url https://graceomolola001-cmyk.github.io/kestrel-pseo/ --max-pages 30 --delay 0.4 --out reports/live.json --html reports/live.html --strict
~~~

The crawler stays on the target host and within the starting URL path, honors robots.txt, limits the number of pages and waits between requests. These defaults are deliberately respectful of live sites.

**For an indexable production site:** Add **--expect-indexable** to flag an unexpected noindex directive. Add **--require-schema** when your page specifications require JSON-LD on every URL.

**Scope:** This is an HTML-based technical monitor. JavaScript-rendered content, comprehensive site crawling, real Google indexation status and rich-result eligibility need additional tools or validation.

### 4. Make schema checking part of every release

The [deployment workflow](../.github/workflows/deploy.yml) runs automated tests, the existing content checks, the HTML QA step and the SEO Operations audit before GitHub Pages deployment.

The schema checker can detect malformed JSON-LD, missing schema context and missing required fields for selected types, including **Article, BlogPosting, Course, FAQPage, BreadcrumbList, Product and Organization**.

For example, if an Article node is missing a headline, author or datePublished value, the audit records a specific schema error. A developer can correct the markup and rerun the release checks.

For production implementations, use [Google's Rich Results Test](https://search.google.com/test/rich-results) for supported rich-result features and Search Console for indexing visibility. JSON-LD syntax and basic field validation are one important layer of technical SEO QA.

### 5. Build a content-refresh queue

Create a list of pages worth reviewing from example Search Console-style data:

~~~bash
python -m seo_ops.cli refresh-queue --input seo_ops/examples/gsc-synthetic.csv --output reports/refresh-queue.csv
~~~

The prioritization uses **impressions, CTR and average position**. It flags, for example, pages ranking around positions 4–20 or earning a low click-through rate. Each recommendation is marked **PENDING_HUMAN_REVIEW** so editors can examine intent, seasonality, titles and content quality before making changes.

These are heuristics for triage, not guaranteed ranking improvements.

### 6. Connect live GSC and GA4 data

The Python connector supports **read-only** exports from Search Console and GA4.

1. Enable the **Search Console API** and **Google Analytics Data API** in your Google Cloud project.
2. Configure Google Application Default Credentials, with permission to access the relevant properties.
3. Install the optional dependencies and run:

~~~bash
pip install -r seo_ops/requirements-optional.txt

python -m seo_ops.cli google-pull --gsc-property 'sc-domain:example.com' --ga4-property '123456789' --output-dir reports
python -m seo_ops.cli refresh-queue --input reports/gsc-pages.csv --output reports/refresh-queue.csv
~~~

For credentials supplied through a JSON file, set the **GOOGLE_APPLICATION_CREDENTIALS** environment variable to its local path. Keep credentials out of Git.

The GSC export includes page URLs, clicks, impressions, CTR and position. GA4 exports daily sessions and key events. Search Analytics API results can be limited to top rows, so completeness should be checked before drawing sitewide conclusions.

### 7. Send audit results to Google Sheets

The [Google Apps Script integration](apps_script/Code.gs) turns the published JSON report into an accessible operating view.

1. Create a Google Sheet, open **Extensions → Apps Script**, and paste the contents of **Code.gs**.
2. In **Project Settings → Script Properties**, set **SPREADSHEET_ID** and **REPORT_URL**. Optionally add **ALERT_EMAIL**.
3. For the Kestrel deployment, use **https://graceomolola001-cmyk.github.io/kestrel-pseo/seo-health.json** as REPORT_URL once Pages is available.
4. Run **syncSeoHealth()** and authorize the script. Run **installDailyTrigger()** once to enable daily updates.

The script writes severity, issue type, affected URL and explanation into a tab named **SEO Health**. It can email newly detected error sets without repeating the same alert after every report timestamp change.

The [weekly GitHub Action](../.github/workflows/seo-ops-monitor.yml) produces its own live-crawl artifacts. For webhook alerts, store **SEO_OPS_WEBHOOK_URL** as a GitHub Actions secret. Without the secret, live findings are still visible in logs and artifacts.

### 8. Plan an SEO conversion experiment

~~~bash
python -m seo_ops.cli experiment seo_ops/examples/experiment-synthetic.json
~~~

The calculator accepts a hypothesis, baseline conversion rate, relative minimum detectable effect (MDE), power and significance threshold. It calculates a **planned sample size per test arm** and evaluates the supplied conversion counts.

When the required sample has not been reached, the result is **inconclusive**, even if the observed conversion lift looks promising. This component supports experiment design and assessment; it does not assign visitors to A/B variants or publish page changes.

The included experiment dataset is **synthetic** so the statistical workflow can be reproduced without sharing client data.

## Using this approach on a real website

For a WordPress, Webflow, SaaS or content-heavy website, the implementation path is:

1. **Define the release requirements:** Which pages must be indexable? Which templates need schema? What canonical patterns are expected?
2. **Connect the publishing workflow:** Use a build output or HTML export for pre-release checks, and adapt the integration to your CMS or deployment system.
3. **Set a permitted crawl scope:** Start with a modest page cap, then expand coverage and alert routing based on site architecture.
4. **Connect analytics and ownership:** Authorize the relevant GSC/GA4 properties; route issues to the person responsible for fixing them.
5. **Keep an editorial approval point:** Use data to shortlist opportunities and let the SEO/content team decide what ships.

The repository is built around a **fictional 24-record education website** and uses synthetic performance/experiment data. It provides a safe environment to run and inspect the automations before connecting them to a live property. The demo site is intentionally noindex.

## Code map

| File | Responsibility |
| --- | --- |
| [cli.py](cli.py) | One command-line interface for audits, crawling, data exports, refresh queues and experiment analysis |
| [core.py](core.py) | HTML/JSON-LD parsing, technical findings and redirect-map checks |
| [crawler.py](crawler.py) | Robots-aware, rate-limited live crawl |
| [google_data.py](google_data.py) | GSC/GA4 API exports |
| [refresh.py](refresh.py) | Editorial refresh-priority scoring |
| [reporting.py](reporting.py) | HTML/JSON dashboards and webhook notifications |
| [experiments.py](experiments.py) | Sample-size planning and conversion-test assessment |
| [apps_script/Code.gs](apps_script/Code.gs) | Google Sheets synchronization and email alerts |
| [tests](tests/) | Automated checks and edge-case coverage |

## Built around a practical SEO principle

**The best automation removes routine friction while making technical decisions visible and auditable.**

That is the approach behind my work across technical SEO, analytics implementation, Apps Script, Python and workflow automation.

**[Read the case study](docs/PORTFOLIO_CASE_STUDY.md)** · **[Explore my portfolio](https://grace-portfolio-1sw.pages.dev/)** · **[See the full repository](../README.md)**
