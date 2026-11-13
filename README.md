# Kestrel eCampus: programmatic SEO practice project

This completed demonstration generates a data-driven static site from a spreadsheet, validates the content, and deploys it through GitHub Actions. It illustrates practical programmatic SEO engineering.
Kestrel eCampus is fictional. Every fee, date and requirement is made up. Nothing here is client data.

[Read the implementation case study](CASE_STUDY.md) for architecture, reproducible validation steps and evidence boundaries.

## What is in this folder

| File | What it is |
|---|---|
| `data/pages.csv` | The dataset. One row per page (24 rows). |
| `data/sources.md` | The "official record". Use it to check every fact. |
| `pseo_checker.py` | Checks the dataset (blanks, formats, copies, stale dates). |
| `build.py` | Turns the dataset into pages in `dist/`. |
| `qa.py` | Checks the built pages (titles, links, canonicals, duplicates). |


You need Python 3.8 or newer. Nothing else to install. Open the repository in your preferred editor and use its terminal.
On Windows, `python` or `py` both work.

## Reproduce the workflow

### Step 1: check the dataset
```
python pseo_checker.py data/pages.csv
```
- FIX means do not publish. REVIEW means a person must confirm it against the source.
- Resolve every item using `data/sources.md`. Two rules:
  1. Never guess a fact. If you cannot confirm it, set `status` to `hold` for that row.
  2. Never change a value just to turn the warning off. Find the true value in the source.
- The checker cannot see everything. After it is clean, compare the remaining rows against `sources.md` yourself.
- Keep notes: for each row you touched, write what the checker said, what the source said, and what you did.
- Done when the checker shows `0 FIX` and you can explain every REVIEW.

### Step 2: build the site
```
python build.py
```
Open `dist/index.html` in your browser. Read five pages as a reader would.

### Step 3: run QA
```
python qa.py
```
Then break something on purpose (for example, change one canonical link in a built page) and run it again.

### Step 4: experiments
- `python build.py --faq-schema` writes FAQ markup. Google stopped showing FAQ rich results on 7 May 2026, so this is for practice and other search engines.
- Set two rows to `hold` and rebuild. Check that they vanish from related links.
- Edit one block of the template in `build.py` and rebuild.

### Step 5: put it online
Upload the `dist/` folder to a free static host (for example Cloudflare Pages direct upload). By default the site is `noindex` and blocks crawlers, which is right for a demo with made-up facts.

### Step 6: document the results
A one-page case study: the goal, the three parts, what the checker found, what only the source could catch, what you held back and why, and the QA results.

## Deploy to GitHub Pages

The file `.github/workflows/deploy.yml` checks the data, builds the site, runs QA, and publishes `dist/` to GitHub Pages.
It stops without publishing if the checker finds a FIX item or QA finds a FAIL.

1. Create a **public** repository (name it `kestrel-pseo`) and put this folder's contents at the repository root.
2. In the repository, go to **Settings, then Pages**, and set **Source** to **GitHub Actions**.
3. Push to the `main` branch, or open the **Actions** tab and run "Check, build and deploy" by hand.
4. When the run is green, your site is at `https://YOUR-USERNAME.github.io/kestrel-pseo/`.

The workflow reads your username and repository name and builds with the right base address, so links and canonical tags are correct on a project site. The site stays `noindex` unless you change the build command to add `--index`.
