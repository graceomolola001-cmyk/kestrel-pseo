# Kestrel: Interview demonstration runbook

This is a **fictional education website and real technical SEO engineering demonstration**. The 24 sample programme records, prices and dates are invented; no business-performance claim should be inferred from them.

## Three-minute screen-sharing walkthrough

1. **Website and programme catalogue**: Open https://graceomolola001-cmyk.github.io/kestrel-pseo/. Show responsive navigation, the programme search filter, and a generated programme page.
2. **Source-controlled generation**: Open build.py and data/pages.csv. Explain how validated records become HTML pages, metadata, canonical tags and internal links.
3. **Pre-release SEO checks**: Open the latest successful run of "Check, build and deploy". Show unit tests, dataset validation, HTML checks, schema checks and redirect review.
4. **Human-readable audit**: Open /seo-health.html and the companion /seo-health.json. Explain how a code-based audit produces both engineer-readable findings and machine-readable data.
5. **Local n8n orchestration**: Import integrations/n8n/kestrel-health-demo.json. Run it with manual trigger. The HTTP Request node retrieves the published audit, the Code node verifies its fields and classifies errors, and the IF node routes the outcome.
6. **Explain live versus test data**: The SEO health checks run on generated HTML. Sample Search Console metrics and experiment input shipped with the repository are explicitly synthetic; the GA4/GSC connector requires authorized Google properties.

## Build and test locally

From the repository root:

~~~bash
python -m unittest discover -s seo_ops/tests -v
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python qa.py dist
python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out dist/seo-health.json --html dist/seo-health.html --strict
python -m seo_ops.cli redirects seo_ops/redirects.csv --strict
~~~

## Why the fictional pages are noindex

All pages are marked with a page-level **noindex** directive by default. The generated robots.txt permits crawling so a compliant crawler can read the directive. On a GitHub **project** Pages website, robots.txt under the project path is not the host-root robots policy. The page-level noindex markup is the index-exclusion control for this demonstration.

The code supports an explicit --index mode for genuine, verified production content. Do **not** switch this fictional demo into indexable mode or present fabricated course information as real admissions offers.

## The audit-to-n8n handoff

- **Source:** https://graceomolola001-cmyk.github.io/kestrel-pseo/seo-health.json
- **Format:** JSON containing target, created_at, pages_checked, counts and findings.
- **Logic:** If errors > 0, route to the failure branch. Otherwise route to the healthy branch.
- **Local n8n:** Works while n8n is running; this example does not require a publicly accessible webhook or cloud hosting.
- **Future extension:** Add Gmail/Slack notifications, deduplication, and GA4/GSC API data ingestion with proper credentials.

## Honest limitations

- HTML checks do not prove Google has indexed or ranked a page.
- The live crawler has a page cap, polite request delay and does not execute client-side JavaScript.
- The sample programme catalogue intentionally contains fictional facts and remains noindex.
- The 24-record website is not evidence of real search acquisition.
- Google API code exists but live extraction requires account access, authorization and data.
- Scheduled monitoring and external alerts should be checked independently before describing them as production-reliable.

## Questions to rehearse

- What triggers a crawl? What are the data sources and outputs?
- What happens when a required canonical, internal link or schema field fails?
- How does a CI failure stop the site deployment?
- How do you distinguish an HTML noindex directive from Google's actual indexing status?
- What would change when scaling from 24 demo records to 500+ validated production pages?
- How do you avoid misreporting analytics events as genuine completed signups?
