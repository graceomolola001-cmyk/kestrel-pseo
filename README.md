# Kestrel | Programmatic SEO & SEO Automation Engineering

**An end-to-end SEO workflow that generates pages from structured content, checks technical health before publication, and automates monitoring after launch.**

**Project owner: Grace Odukoya**  
SEO specialist • Technical SEO • Python & Google Apps Script • Automation engineering • Growth analytics

[Explore the SEO Operations Control Center](seo_ops/README.md) · [Read the technical case study](seo_ops/docs/PORTFOLIO_CASE_STUDY.md) · [View automated tests and deployments](../../actions)

## Why I built this

SEO teams often face the same operational bottleneck: publishing and maintaining many pages takes time, and small technical mistakes can spread across a website before someone spots them.

Kestrel demonstrates how I approach that problem as an SEO automation specialist. I combine **content systems, technical SEO, scripting and quality assurance** to make website operations more reliable and easier to scale.

The workflow helps a team answer three practical questions:

1. **Can this content be published?** Validate the source data, page templates, metadata and links before pages go live.
2. **Did the release introduce SEO risks?** Check titles, canonical URLs, structured data (JSON-LD), indexability rules and redirects automatically.
3. **Where should the team focus next?** Surface issues in reports and identify content-refresh candidates from Search Console data.

## What the system does

| Capability | Business value | Technical implementation |
| --- | --- | --- |
| Programmatic SEO page generation | Produce consistent pages from structured content while keeping editorial checks in place | Python, CSV, HTML templates |
| Pre-publication quality checks | Catch missing metadata, broken internal links and template errors before release | Data validator, HTML QA, CI |
| Schema markup validation | Detect malformed JSON-LD and missing essential fields for supported schema types | Python HTMLParser and JSON parsing |
| Automated crawl monitoring | Flag common technical SEO problems on accessible live URLs | Robots-aware, rate-limited crawler |
| Redirect-map auditing | Identify redirect loops, chains and duplicate mappings before migrations | CSV-based redirect graph checks |
| SEO health reporting | Give stakeholders a clear view of errors, warnings and pages checked | HTML and JSON reports, optional Google Sheets |
| Search-driven content prioritization | Create an actionable review queue for editors | GSC export and scoring rules |
| Conversion experiment planning | Estimate sample-size requirements and evaluate results conservatively | Fixed-horizon A/B test calculator |

The **SEO Operations Control Center** contains the monitoring, schema, reporting, Google API and automation modules. [See how each module works and reproduce it](seo_ops/README.md).

## How the workflow fits together

~~~text
Structured content (CSV)
        |
        v
Data validation → Page generation → HTML / SEO / JSON-LD checks
                                         |
                              PASS → GitHub Pages deployment
                              FAIL → Release blocked for correction
                                         |
                                         v
                            Scheduled, bounded live crawl
                                         |
                                         v
                            SEO health report + alert hooks

Optional integrations:
Search Console + GA4 → data exports → human-reviewed content refresh queue
Published health report → Apps Script → Google Sheets + email alerts
~~~

The automation follows an operational principle I use in SEO engineering: **catch predictable errors with code, then reserve human attention for judgment and improvements.**

## Reproduce the working demo

**Requirements:** Python 3.10 or later and Git. The core build and audit use the Python standard library.

~~~bash
git clone https://github.com/graceomolola001-cmyk/kestrel-pseo.git
cd kestrel-pseo

# Run the existing tests
python -m unittest discover -s seo_ops/tests -v

# Verify the content dataset and generate the website
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python qa.py dist

# Audit the generated pages and validate redirect mappings
python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out reports/prepublish.json --html reports/prepublish.html --strict
python -m seo_ops.cli redirects seo_ops/redirects.csv --strict

# Build an editorial queue from example Search Console-style data
python -m seo_ops.cli refresh-queue --input seo_ops/examples/gsc-synthetic.csv --output reports/refresh-queue.csv
~~~

Open **reports/prepublish.html** to inspect the SEO findings. For deeper instructions covering live crawling, Google APIs, Apps Script and experiment planning, see the [developer guide](seo_ops/README.md).

## Verified engineering evidence

- **14 automated tests** cover structured-data checks, redirect edge cases, local auditing, human review gating and experiment logic.
- **GitHub Actions** runs tests and pre-publication SEO checks as part of the deployment workflow.
- A separate **scheduled/live monitoring workflow** can crawl the published site and upload audit reports.
- Every generated report contains specific findings that a developer or SEO specialist can act on.

[Inspect the deployment workflow](.github/workflows/deploy.yml) · [Inspect the monitoring workflow](.github/workflows/seo-ops-monitor.yml) · [Browse tests](seo_ops/tests)

## Project and data context

Kestrel eCampus is a **fictional education website** created to provide a safe, reproducible SEO engineering environment. Its 24 source records and example analytics are illustrative. The site is intentionally configured with **noindex** to avoid presenting invented programme details as real search results.

Core validation and deployment checks are implemented and tested. Live GSC/GA4 extraction, Google Sheets sync and external alerts are available as **permissioned integrations** and require the destination accounts and credentials to be configured.

## About the builder

I work at the intersection of **SEO strategy, technical implementation, analytics and automation**. My focus is designing systems that reduce repetitive work, make measurement more dependable and give content and growth teams clearer decisions.

My wider work includes SEO content strategy, GA4/GTM conversion measurement, Google Apps Script, Python, workflow automation with n8n/Make, and programmatic content systems.

**[Explore my portfolio](https://grace-portfolio-1sw.pages.dev/)** · **[View the full SEO automation implementation](seo_ops/README.md)**
