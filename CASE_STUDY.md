# From a CSV to a checked, deployable programmatic SEO site

## The problem

Scaling location-specific programme pages is tempting: duplicate a template, swap the country, and publish. But a single wrong fee, intake, or canonical URL can spread across dozens of URLs. Kestrel eCampus is a **fictional** university used to demonstrate how to put validation ahead of publication.

## What the implementation actually does

The source-of-truth file is `data/sources.md`; the structured page inputs are in `data/pages.csv`. `pseo_checker.py` checks data quality and flags cases for human review. `build.py` produces programme detail pages, a programme hub and a homepage with internal links and SEO metadata. `qa.py` inspects the generated HTML for titles, descriptions, headings, canonicals, internal links, structured-data consistency and near-duplicate records.

The GitHub Actions deployment runs the checks before deploying to Pages. The demo deliberately defaults to `noindex` because its university and facts are invented.

## Reproduce in three commands

```bash
python pseo_checker.py data/pages.csv
python build.py
python qa.py dist
```

Inspect `dist/index.html`, then change a canonical on a generated HTML file and rerun QA. The checker should flag that discrepancy. Restore by rebuilding.

## Acceptance criteria

- No unresolved blocking data errors before the build.
- Every published page has an appropriate self-referencing canonical.
- Internal links resolve within the generated output.
- Held records do not appear as published programme pages.
- Fictional content remains nonindexable.

## What this proves, and what it does not

This project demonstrates a repeatable pSEO publishing architecture, data checks and static deployment. It is a practice project: it does not establish search visibility, rankings, conversion improvements or client results.

## Next improvements

Add fixture-based unit tests, automated accessibility checking, and a documented data-change review log.
