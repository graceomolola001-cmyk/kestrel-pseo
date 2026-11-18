# Kestrel: live GA4 + GSC + SEO audit in local n8n

This workflow runs **real authenticated Google API requests** using the service account you already verified through the Python `google_probe` command. It also fetches the published technical SEO audit from Kestrel.

Import: [kestrel-google-apis-demo.json](../integrations/n8n/kestrel-google-apis-demo.json)

## What it does

```text
Manual Trigger
  → GA4 Data API (daily sessions and page views)
  → GA4 Realtime API (active users now)
  → Search Console API (page-level search performance)
  → Published Kestrel audit (technical checks)
  → Code (validates and summarizes REAL responses)
  → IF (technical errors?)
     ├── needs review
     └── no critical errors in checked scope
```

It is a **manual demonstration** until you add a schedule and an actual notification destination. The final branch nodes deliberately do nothing: connecting an email or Slack alert remains a separate follow-up.

## 1. Start local n8n

Check that Node.js and npm work in your PowerShell terminal:

```powershell
node --version
npm --version
npx n8n
```

Open http://localhost:5678 and finish your local setup. Keep n8n running while using the workflow.

## 2. Import the workflow

1. Open the repository JSON file linked above and download the **raw** file, or use the copy inside your latest extracted Kestrel repo.
2. In n8n, create a new workflow and choose **Import from File** in the workflow menu.
3. Select `integrations/n8n/kestrel-google-apis-demo.json`.
4. Save the workflow.
5. Do not expect it to run before you configure the Google credential.

## 3. Configure one Google service-account credential

1. In n8n **Credentials**, create a **Google Service Account API** credential.
2. Copy the required **Service Account Email** and **Private Key** from your downloaded Google Cloud JSON, inside the *local credential manager only*. Do **not** paste them into workflow node fields, GitHub, this chat, or screenshots.
3. Enable **Set up for use in HTTP Request node** if offered.
4. Specify both read-only scopes:
   - `https://www.googleapis.com/auth/analytics.readonly`
   - `https://www.googleapis.com/auth/webmasters.readonly`
5. Save and test the credential. The service-account identity already has the required GA4 Viewer and GSC Restricted access.
6. Open each of the **GA4 Data API**, **GA4 Realtime API**, and **Search Console API** HTTP Request nodes. Select **Predefined Credential Type → Google Service Account API**, and choose the same saved credential.

There are **no secrets** inside the importable JSON. The OAuth access token is handled by n8n at execution time.

### n8n setup difference

Some n8n releases show the "Google Service Account API" credential type directly under the HTTP Request node, while others require creating it first in Credentials. If a node says it cannot find or use the credential, reselect that credential in the node, and ensure the HTTP Request option and scopes are enabled.

## 4. Execute and inspect

Visit https://graceomolola001-cmyk.github.io/kestrel-pseo/ in a normal browser to produce a genuine visit, then click **Execute workflow**.

Inspect the outputs in order:

- **GA4 Data API:** valid response even if `rows` is missing or empty. Requests the last seven days through today, with `date`, `sessions`, and `screenPageViews`.
- **GA4 Realtime API:** requests `activeUsers` for the recent realtime window. It can be zero if no users are currently active.
- **Search Console API:** requests page-level search data for the period ending three days ago. Kestrel is noindex; zero rows are expected.
- **Published SEO audit:** a live public JSON report with `counts.error`, `counts.warning` and `pages_checked`.
- **Build verified SEO report:** summarizes returned rows and actual totals, without inventing numbers.
- **Any technical errors?:** routes to a human review branch when the audit includes errors.

A successful workflow run demonstrates Google API authorization and parsing, plus the technical QA-to-workflow handoff. It does **not** establish that Kestrel has organic traffic, real leads or a production-grade notification service.

## 5. Interview demonstration

Say:

> "I built a Python programmatic SEO publishing system. GitHub Actions checks generated pages before deployment and produces a machine-readable audit. I also configured a Google Cloud service account with read-only GA4 and Search Console access. This n8n workflow authenticates to both APIs, requests the latest data, fetches the Kestrel audit and routes any technical errors. Because this is a new noindex demo, I report zero Search Console rows clearly rather than creating false traffic."

Show the three HTTP Request nodes, the Code node and the final IF branch. You can show the Google property IDs, API endpoints and result counts. **Do not** show the private key, credential editor, downloaded JSON, or authorization headers.

## Troubleshooting

| Result | Likely explanation | Next check |
| --- | --- | --- |
| 401 / 403 at GA4 | The selected service account or scope is wrong | Check the node credential, Analytics API and GA4 Viewer role |
| 401 / 403 at GSC | Incorrect service account permissions or scope | Check GSC Restricted permission and `webmasters.readonly` |
| GA4 daily rows: zero | Reporting data is still processing or the range has no data | Compare Realtime and the standard GA4 report |
| GA4 realtime active users: zero | No active visitors in the recent realtime window | Visit the website, then rerun |
| GSC rows: zero | New noindex demo has no search performance | This is expected; the call can still succeed |
| 404 for audit JSON | The published audit URL changed or site is unavailable | Open the URL directly in a browser |
| Workflow stops before Code | A Google API or published audit request failed | Inspect the failing HTTP node output |

Official references:
- https://docs.n8n.io/integrations/builtin/credentials/google/service-account/
- https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-basics
- https://developers.google.com/analytics/devguides/reporting/data/v1/basics
- https://developers.google.com/webmaster-tools/v1/searchanalytics/query
