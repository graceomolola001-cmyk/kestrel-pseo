# Editorial interface and interactive demo

Kestrel's website is a **fictional content dataset with real publishing and QA code**. Its interface illustrates the operational model and provides inspection of actual artifacts.

## Design goals

- Visual identity: warm paper, dark ink, restrained teal/citrus highlights, serif editorial display typography, mono labels for engineering details.
- Distinctive composition: asymmetric hero and angled live-audit board, careful typography and intentional contrast.
- Purposeful movement: animated data flow, ticker and entrance transitions; respects \`prefers-reduced-motion\`.
- Useful interactions: text search, country filters, accessible tab-based issue simulator, actual published SEO report.
- Built for performance: no remote UI frameworks, no fonts/CDNs needed for the frontend, cacheable CSS and JS.
- No fake social proof, fabricated "live" marketing KPIs or deceptive CTA.

## Genuine vs simulated information

**Actual pipeline**
- Python source data and generated site pages
- Automated tests and GitHub Actions release gate
- /seo-health.json and /seo-health.html from real build-time QA of the fictional site
- Published audit counts are fetched client-side; fetch failures are shown as failures instead of fabricated numbers

**Simulated educational examples**
- The three SEO issue tabs demonstrate hypothetical noindex, canonical and broken-link mistakes.
- These are predefined examples for explaining diagnostic logic. They do **not** execute remote crawls and must never be presented as detected live incidents.
- All course data is fictitious and pages remain noindex.

## File map

- \`build.py\`: generates static HTML pages and copies UI assets
- \`site_assets/site.css\`: responsive design and motion
- \`site_assets/site.js\`: accessible UI interactions and read-only audit fetch
- \`.github/workflows/deploy.yml\`: JavaScript syntax validation, SEO tests and deployment
- \`seo_ops/tests/test_demo_build.py\`: validates public asset paths and core demo elements

## How to present it

1. Explain the content and technical SEO operations problem.
2. Open Kestrel and filter a programme by country.
3. Show the live audit board and click through to the JSON or HTML report; be explicit that the page data itself is fictional.
4. Open the interactive failure simulator and select the accidental noindex case. Explain the underlying expected-indexability baseline rule.
5. Show GitHub Actions and explain the release gate, test failures and repair workflow.
6. Discuss real GA4/GSC API integration separately, only after it has been authorized and successfully tested.

## Accessibility and reliability

- Native links, buttons and inputs work with keyboard input.
- Scenario tabs support arrows, Home and End keys.
- Search result counts use a live region.
- Reduced-motion support removes automatic transitions and animation.
- Dynamic audit data is loaded only from the published JSON report. The initial state says it is loading, and errors have an explicit unavailable state.
