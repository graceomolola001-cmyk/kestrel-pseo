# Kestrel: 500-page programmatic SEO scale test

## Why the extra pages stay offline

The public Kestrel website has 24 fictional programme records and a small set of service pages.
Adding 500 near-identical fictional pages to the live site would not demonstrate better rankings,
and could mislead readers who think the programmes are genuine.

For technical interviews, the useful proof is the ability to **generate 500 unique URLs, validate
their HTML, inspect duplicate risks, check noindex, and stop failures before publication.**

The 500 generated test pages are written to **reports/scale-test/site**, ignored by Git.
They are never placed in the GitHub Pages published \`dist\` directory.

## Run the real 500-page test on Windows

From the top-level Kestrel folder in VS Code PowerShell:

~~~powershell
python -m seo_ops.scale_test --count 500
~~~

This runs the real Kestrel pipeline:

1. Create 500 unique, fictional rows with valid country-currency pairs and synthetic sources.
2. Feed the CSV to \`build.py\`, the same static HTML generator used by the public site.
3. Run \`qa.py\` against every resulting HTML file, including internal links and duplicate checks.
4. Run the \`seo_ops.core.audit_directory\` technical SEO audit.
5. Assert there are **505 HTML pages** (500 generated cases + the 5 site sections), 505 unique canonical URLs, and page-level noindex directives.
6. Inject an **explicitly simulated indexability mistake** into a test audit expectation. Confirm that \`UNEXPECTED_NOINDEX\` is detected.
7. Save \`summary.json\` and \`seo-audit.json\` under \`reports/scale-test\`.

You can also run a small smoke test:

~~~powershell
python -m seo_ops.scale_test --count 8 --out reports/small-scale-test
~~~

This is **fictional content at scale**. These pages do not represent real university programmes,
published SEO acquisition, actual users, or proof that Google indexed them.

## Run it in GitHub Actions

Open **Actions → Synthetic pSEO 500-page scale test → Run workflow**.

The workflow runs on GitHub's own runner and provides a downloadable \`synthetic-500-page-test-evidence\`
artifact containing the summary and audit output. It also runs on pull requests that change
the scale-test code.

This is an optional, separate benchmark. The ordinary site deployment builds only the
approved small website.

## What an interview demonstration can show

- Structured input: the generated CSV has 500 unique programme-country keys.
- Automation: a single Python command builds all pages and runs QA.
- Quality gate: the generated pages receive self-referencing canonicals and noindex signals.
- Failure injection: one intentionally different indexability expectation triggers the checker.
- Results: the summary reports exact pages checked and error/warning counts.

The test currently checks **HTML structure and operational safeguards**. It cannot prove that
the sample content is original or valuable to searchers. Real large-scale SEO publishing needs
genuine source information, clear intent, editorial review, and content that deserves to exist.

## Photographic content on the public site

Three editorial images are sourced from Unsplash's free-to-use licensed photographs. Each
has visible attribution, descriptive alt text, explicit image dimensions and lazy loading.

- Lau Clrd: workspace — https://unsplash.com/photos/laptop-notebook-and-coffee-on-a-desk-srrvlsaB2P4
- Vitaly Gariev: studying/work — https://unsplash.com/photos/young-woman-working-on-a-laptop-at-home-WrevB3gLLBs
- Dawit: programming laptop — https://unsplash.com/photos/laptop-displaying-code-on-a-desk-dTmj5aXbKp4

They are **illustrative photos**, not photographs of Kestrel students, staff or facilities.
The image files are served from Unsplash's CDN and can be optimized or self-hosted in the future.
