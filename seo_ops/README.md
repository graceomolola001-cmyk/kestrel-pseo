# Kestrel SEO Operations Control Center

**Python + APIs + Google Apps Script + GitHub Actions | release gates, structured-data checks, crawl monitoring and content prioritization**

This is a *reproducible engineering demonstration* built around [Kestrel eCampus](../README.md), a fictional programmatic SEO website. It extends a real static-site pipeline with repeatable SEO monitoring and release QA. Kestrel's business facts, traffic examples and experiment counts are fictional. See [case study](docs/PORTFOLIO_CASE_STUDY.md) for truthful evidence boundaries.

## At a glance

| Automation | Implementation | Evidence |
| --- | --- | --- |
| Pre-release schema checks | JSON-LD parse + `@graph` + type-specific required fields, in CI | `core.py`, tests |
| Crawl and SEO signals | Robots-aware, same-site, bounded crawler, canonicals, title/H1/noindex, HTTP failures | `crawler.py`, GitHub Action |
| Migration/redirect QA | CSV review for duplicates, self-redirects, chains, cycles and cross-host changes | `core.py`, tests |
| GSC + GA4 extracts | Read-only official APIs with Google ADC credentials and real property access | `google_data.py` (optional setup) |
| Analytics for writers | GSC-derived refresh queue, deliberately gated by human review | `refresh.py` |
| Dashboard + alerts | Generated HTML and JSON; optional webhook; Apps Script to populate Sheets/email on new errors | `reporting.py`, `apps_script/Code.gs` |
| Experiment methodology | Pre-specified relative MDE, power, alpha, per-arm sample size, fixed-horizon test, honest inconclusive result | `experiments.py`, synthetic example |
| Safety | No private business data, no API keys in git, strict CI failures on errors; local test coverage | `tests/`, Actions |

## Quick start (no paid software)

From the **repository root**, with Python 3.10+ installed:

```bash
python -m unittest discover -s seo_ops/tests -v
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out reports/prepublish.json --html reports/prepublish.html --strict
python -m seo_ops.cli redirects seo_ops/redirects.csv --strict
python -m seo_ops.cli refresh-queue --input seo_ops/examples/gsc-synthetic.csv --output reports/refresh-queue.csv
python -m seo_ops.cli experiment seo_ops/examples/experiment-synthetic.json
```

The demo deploy pipeline runs the prepublish audit automatically and publishes `seo-health.json` and `seo-health.html` alongside the site. The separate **SEO Ops live monitor** Action can be triggered manually or on its schedule to crawl the deployed site. Live reports are uploaded as artifacts, not silently written into the repository. If GitHub Pages is not configured, live crawling will fail until the site is deployed.

For a live check of a site you **own or have permission to crawl**:

```bash
python -m seo_ops.cli crawl --url https://graceomolola001-cmyk.github.io/kestrel-pseo/ --max-pages 30 --out reports/live.json --html reports/live.html --strict
```

Robots rules are honored. Only URLs under the supplied start-path on the same host are queued. It is deliberately low-volume and single-threaded. This is not a substitute for Screaming Frog/Sitebulb's exhaustive crawling, nor does it confirm Google indexation.

### Schema limitations

JSON-LD checking supports common `@type` structures and catches malformed JSON, missing `@context` and essential fields for selected types. It does **not** validate every schema.org relationship, render JavaScript, establish compliance with Google content policies or certify rich-result eligibility. Confirm rich-result eligibility using Google's Rich Results Test and evaluate indexation with Search Console. The example site is intentionally `noindex`, so the default demo does **not** flag noindex as an error. Use `--expect-indexable` for an indexable production site; use `--require-schema` if every page must contain JSON-LD.

### GSC + GA4 integrations

Set up a Google Cloud project, enable **Search Console API** and **Google Analytics Data API**, configure Google Application Default Credentials with actual property permissions, then:

```bash
pip install -r seo_ops/requirements-optional.txt
# Set GOOGLE_APPLICATION_CREDENTIALS to an untracked credentials JSON file (or use ADC)
python -m seo_ops.cli google-pull --gsc-property 'sc-domain:yourdomain.com' --ga4-property '123456789' --output-dir reports
python -m seo_ops.cli refresh-queue --input reports/gsc-pages.csv --output reports/refresh-queue.csv
```

Exports are created only when authenticated requests succeed. No GSC/GA4 production results are included in this repository. The GSC Search Analytics API may return only top rows, so do not interpret exports as a complete census. `keyEvents` follows GA4 event setup in the real property.

### Google Sheets via Apps Script

1. Create a Google Sheet; open **Extensions > Apps Script** and paste [`apps_script/Code.gs`](apps_script/Code.gs).
2. Set **Project Settings > Script Properties**: `SPREADSHEET_ID`, `REPORT_URL` and optionally `ALERT_EMAIL`. For this demo, `REPORT_URL` is `https://graceomolola001-cmyk.github.io/kestrel-pseo/seo-health.json` once Pages has deployed.
3. Run `syncSeoHealth()` and authorize the script. Run `installDailyTrigger()` once to install a daily sync. It deduplicates alerts by the actual set of errors, not the run timestamp.
4. Google Sheets is the reporting destination. Publishing and changes remain under human control.

### A/B experiment rigor

The experiment utility calculates the **planned sample size per arm** before launch and then evaluates conversion counts. If the planned sample size is unmet, it reports *inconclusive* even when a large lift is visible. The included sample is clearly marked **SYNTHETIC** and is not an actual test result. Use genuine, pre-registered tests and documented results when discussing past experiment experience.

### Notifications and operational limits

The live monitor accepts an optional `SEO_OPS_WEBHOOK_URL` (Slack-compatible JSON webhook) stored in GitHub Actions secrets. Without a webhook, findings remain in Actions logs and artifacts. Scheduled Actions can be delayed, and GitHub disables schedules in inactive public repositories after 60 days. The site must actually be deployed to collect a live audit. No credentials or proprietary client data should be committed.

## Evidence map for an interview

- **Show the code working:** trigger the live monitor, download its JSON/HTML artifact, intentionally corrupt a JSON-LD fixture in a branch and show a failing test.
- **Discuss the architecture:** the static-site build gates publication, live site checks run separately, an optional Apps Script moves reports into Sheets, and GSC/GA4 are explicit permissioned integrations.
- **Discuss business impact responsibly:** reduces repetitive manual checks in a demo pipeline. Time saved, incidents prevented, organic lift and production uptime are **not measured** here.
- **Discuss ACOS separately:** ACOS is an earlier content categorization/internal-linking system in development. Do not describe its Make.com implementation as fully deployed unless it was.

The code is a portfolio artifact. It cannot substitute for calendar years of employment or documented migrations, 500+ page ownership, or actual A/B test outcomes.
