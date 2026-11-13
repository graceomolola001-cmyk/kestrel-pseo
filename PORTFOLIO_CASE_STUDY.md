# Case study: building a reproducible programmatic SEO pipeline

## The problem

A site with many combinations of programmes and locations can accumulate repetitive manual content work and inconsistent facts. The fictional Kestrel eCampus exercise models that challenge using a spreadsheet rather than a client's confidential data.

## The approach

1. **Source of truth:** `data/sources.md` supplies reference facts and `data/pages.csv` contains 24 candidate page rows.
2. **Quality gate:** `pseo_checker.py` detects missing fields, formatting errors and data needing manual review.
3. **Publication controls:** `build.py` publishes only rows marked `publish`; unresolved records can remain on `hold`.
4. **Search structure:** the generator creates titles, descriptions, canonical URLs, human-readable URLs, relevant links and optional FAQ structured data.
5. **Release quality:** `qa.py` inspects generated HTML, page metadata, duplicate fields, internal links and sitemap consistency. GitHub Actions runs the checks before deployment.

## Reproduce

```bash
python pseo_checker.py data/pages.csv
python build.py
python qa.py dist
```

Open `dist/index.html` to inspect the generated website. By default the fictional demo uses `noindex`; that is intentional. For a GitHub Pages preview, use the repository deployment workflow.

## What to learn

The critical engineering choice is to **withhold uncertain content** rather than turn every spreadsheet row into a live URL. Automated validation catches format and consistency problems; human review still owns factual accuracy.

## Evidence and limits

The repository contains the source data, code and QA procedures, so a reader can reproduce the build. This is a fictional demonstration, with no claim of real-user traffic, ranking gains or revenue. Add your own screenshots and dated QA log after reproducing the workflow.
