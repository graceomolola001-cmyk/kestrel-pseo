# Kestrel: pages and folders

Kestrel is a real, multi-page static website. Python builds every HTML file. GitHub Pages publishes the files in folders so each page has its own web address.

## Page map

| Folder | What visitors find |
| --- | --- |
| \`/\` | Home: what the lab does, real audit summary, and links to the main sections |
| \`/about/\` | Why the project was built |
| \`/systems/\` | Overview of the technical tools |
| \`/systems/release-gate/\` | How Kestrel checks pages before publishing |
| \`/systems/live-monitoring/\` | How the crawler checks pages and writes reports |
| \`/systems/google-apis/\` | How the GA4 and Search Console connectors work |
| \`/lab/\` | Interactive examples of common SEO problems |
| \`/case-studies/kestrel/\` | Project story and links to real code |
| \`/programmes/\` | Searchable sample course pages |
| \`/programmes/online-.../\` | One generated HTML page for each course and country |
| \`/assets/\` | Shared CSS and JavaScript |

A folder like \`/systems/live-monitoring/\` contains its own \`index.html\` file. You can open that URL directly, share it, or link to it from another page.

## Colour system

The site uses the user's Prism Authority colours:
- Imperial Iris: #533E80
- Deep Teal: #166D73
- Amber: #E9AC4E
- Porcelain: #F8F6F1
- Night Ink: #171923

Use Iris for key headings and navigation, Teal for secondary details, Amber with Night Ink text for key buttons, Porcelain for reading surfaces, and Night Ink for dark panels.

The site uses common system fonts, clear spacing and motion that responds to the user's reduced-motion setting. No paid hosting, custom font or JavaScript framework is required.

## Plain-English writing rules

- Keep most sentences short.
- Explain technical terms when readers first meet them.
- Use examples and clear actions.
- Avoid buzzwords, unsupported claims and made-up success metrics.
- Keep labels useful for readers and interviewers.
- State clearly which content is fake and which tests have truly run.

## Data integrity

This is a fictional education website. Its course details are made up. The pages are marked noindex by default.

Actual code, tests and deployment reports are available through GitHub. The lab issue examples are simulations. GA4 and GSC APIs require real authorization and may return little or no data for a new noindex demo.

## Build and test

\`\`\`bash
python -m unittest discover -s seo_ops/tests -v
python pseo_checker.py data/pages.csv
python build.py --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo
python qa.py dist
python -m seo_ops.cli audit-dir dist --base-url https://graceomolola001-cmyk.github.io/kestrel-pseo --out dist/seo-health.json --html dist/seo-health.html --strict
\`\`\`

The CI workflow also runs \`node --check site_assets/site.js\`.

## Interview use

1. Open the homepage and explain what Kestrel checks.
2. Open **Systems → Release gate** and show the test steps.
3. Open **The lab** and try an example SEO problem.
4. Open **Page library**, search a country and open a generated page.
5. Show an actual GitHub Actions run and the published JSON report.
6. Explain how Google APIs and local n8n can connect when authorized.
