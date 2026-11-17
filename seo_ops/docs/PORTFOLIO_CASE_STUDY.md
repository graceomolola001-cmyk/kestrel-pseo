# Case study | Building an automated technical SEO quality-control system

**Kestrel SEO Operations Control Center**  
**Project owner:** Grace Odukoya  
**Focus:** Technical SEO, programmatic SEO, automation engineering and growth measurement  
**Stack:** Python, JSON-LD, Google Apps Script, Google Sheets, Google APIs, HTML/CSS, GitHub Actions  
**Project date:** November 2026

[Explore the source code](../../README.md) · [Read the developer guide](../README.md) · [Review the release workflow](../../.github/workflows/deploy.yml)

## The operational challenge

Imagine a growing content or SaaS company releasing pages regularly across multiple templates. Each release introduces opportunities for technical issues: missing title tags, conflicting canonical URLs, malformed structured data, duplicate metadata, unexpected noindex directives or redirect errors.

Those problems can be easy to miss when QA depends on a long manual checklist. Meanwhile, content and growth teams still need to prioritize updates and measure conversion performance.

**The objective:** Build a repeatable SEO operations workflow that checks pages before release, monitors technical signals after launch and puts findings in front of the people who can act on them.

## My approach

I organized the system around three operational checkpoints:

| Checkpoint | Operational question | Automated response |
| --- | --- | --- |
| **Before publishing** | Are these pages technically ready to ship? | Validate source data, generated HTML, metadata, internal links and JSON-LD; block the release when errors are detected |
| **After publishing** | Did the live site develop new technical risks? | Run a polite, bounded site crawl and save a readable SEO health report |
| **During optimization** | Which pages deserve investigation and which experiments need more evidence? | Use GSC-derived page signals to build a human-reviewed refresh queue and calculate A/B test sample requirements |

This structure protects quality while keeping SEO specialists involved where judgment is essential.

## What I implemented

### 1. An SEO quality gate inside the publishing workflow

A Python audit checks generated pages for key SEO elements. It parses JSON-LD structured data, including graph-based structures, and verifies required fields for selected types such as Article, Course, Organization and BreadcrumbList.

**Why it matters:** A developer receives a specific error before publishing the page, instead of discovering the problem during a later SEO audit.

The checks run in [GitHub Actions](../../.github/workflows/deploy.yml) alongside the programmatic site generator. Errors can stop deployment; warnings remain available for review.

### 2. Live crawl monitoring and transparent reports

A second workflow can crawl the published site within a defined URL scope. It honors robots.txt, limits request volume, and checks accessible pages for HTTP errors and common SEO signals.

The reporting layer generates **JSON for automation** and **HTML for people**. Findings include a severity, issue code, affected URL and explanation.

**Why it matters:** A founder or content manager can understand what needs attention without interpreting raw Python logs.

### 3. Redirect-map and migration preparation checks

The migration checker reads a CSV of source and destination URLs. It identifies duplicate mappings, self-redirects, redirect chains, cycles and potential cross-domain moves.

**Why it matters:** Teams can review risky redirects before applying a migration plan. Live redirect behavior and post-launch ranking protection require additional deployment-specific testing.

### 4. A data-to-decision workflow for content teams

A Search Console exporter retrieves page-level search performance through the official API, when credentials and property permissions are provided. A separate scoring module uses impressions, CTR and average position to shortlist potential refreshes.

Every queued recommendation carries a **PENDING_HUMAN_REVIEW** status.

**Why it matters:** Editors spend less time assembling a starting list and retain control over strategy, relevance and publishing.

The GA4 extractor retrieves daily sessions and key events. The Apps Script module can copy published audit findings into Google Sheets and send email alerts for new error sets.

### 5. Evidence-led experiment planning

The conversion experiment utility estimates sample size per arm from a baseline rate, minimum detectable effect, significance threshold and power. It evaluates supplied conversion results against those preselected requirements and can return an **inconclusive** result when evidence is insufficient.

**Why it matters:** A team can document the standard for a decision before interpreting a lift in conversion rates.

## Engineering proof and reproducibility

The implementation contains **14 automated tests** across structured-data parsing, redirects, HTML auditing, content-review status and experiment rules. The release checks are integrated into the GitHub deployment workflow, which has completed successfully.

Run the system from the repository root:

~~~bash
python -m unittest discover -s seo_ops/tests -v
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python qa.py dist
python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out reports/prepublish.json --html reports/prepublish.html --strict
python -m seo_ops.cli redirects seo_ops/redirects.csv --strict
~~~

The [technical README](../README.md) documents how to enable bounded crawling, GSC/GA4 data pulls, a Sheets dashboard, optional alerts and the content refresh queue.

## What the project establishes

**Delivered:** A functioning SEO automation architecture with reusable checks, explicit release-failure rules, reporting outputs and a reproducible test suite.

**Demonstrated:** The ability to translate recurring SEO processes into scripts and workflows, integrate technical QA with a content publishing pipeline, and design reporting for both technical and commercial stakeholders.

**Data environment:** Kestrel eCampus is a fictional 24-record website. Example search and experiment datasets are synthetic. Real-site integrations are permissioned configuration steps, and the demo remains noindex. This keeps the implementation independently inspectable without exposing client data or misrepresenting performance outcomes.

## A production rollout would build on this foundation

For a larger WordPress, Webflow or SaaS site, I would start by documenting its publishing process, page templates, critical conversion paths and SEO acceptance criteria. Then I would adapt the checks to the deployment platform, connect authorized analytics properties, define crawl coverage and route errors to owners.

After launch, I would measure coverage, issue detection and resolution time before reporting operational impact. Site migration releases would include redirect testing on staging, launch-day verification and post-release Search Console monitoring.

## My working principle

**Automate the predictable. Make SEO risks visible. Keep human judgment where it creates the most value.**

That is how I approach technical SEO, analytics and workflow engineering: connect the underlying process to a reliable system that people can understand, inspect and improve.

**[View the implementation](../README.md)** · **[Explore my portfolio](https://grace-portfolio-1sw.pages.dev/)**

### References for further technical validation

- [Google Search Console API](https://developers.google.com/webmaster-tools/v1/api_reference_index)
- [Google structured-data guidance](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [GitHub Actions workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
