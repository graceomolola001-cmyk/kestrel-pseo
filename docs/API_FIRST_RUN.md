# Kestrel: first real GA4 and Search Console API test

**Already completed**: GA4 website tag installed and confirmed in Realtime; Kestrel Search Console property verified. You do not need another GA4 property or another Search Console property.

This guide is for **API authentication**, so Python and local n8n can fetch the data using authorized Google credentials.

## Public Kestrel identifiers
- GA4 web Measurement ID: `G-K3E3Z1C089` (browser tracking)
- GA4 numeric Property ID: `565038230` (Data API)
- Search Console URL-prefix property: `https://graceomolola001-cmyk.github.io/kestrel-pseo/` (Search Console API)

## Part 1. Google Cloud project and APIs

1. Open https://console.cloud.google.com/projectcreate and create a Google Cloud project, e.g. **Kestrel SEO Lab**. The name is only an example.
2. In the same selected project, enable the **Google Analytics Data API**:
   https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com
3. Enable the **Google Search Console API**:
   https://console.cloud.google.com/apis/library/searchconsole.googleapis.com
4. Open **IAM & Admin → Service Accounts**:
   https://console.cloud.google.com/iam-admin/serviceaccounts
5. Create a service account named `kestrel-seo-reader`. Note the generated email, ending with `.iam.gserviceaccount.com`.
6. For this read-only exercise, no broad Google Cloud IAM project role is required for property data access. Grant access **inside GA4 and Search Console** as described next.

## Part 2. Give the service account limited access

1. In GA4, select numeric property **565038230**. Go to **Admin → Property access management → Add users**.
2. Add the service-account email as a **Viewer**.
3. In Search Console, select the exact Kestrel URL-prefix property. Go to **Settings → Users and permissions → Add user**.
4. Add the same service-account email with **Restricted** or another permitted read-only user role. API access requires property read permission.

If Google refuses a service-account address in a particular interface, stop and use a user-based OAuth flow instead. Do not grant broad Owner or project Editor permissions merely to work around the error.

## Part 3. Store credentials privately on your Windows laptop

For local automation you can create a service-account JSON key from **Google Cloud → IAM & Admin → Service Accounts → Keys → Add key → Create new key → JSON**, if permitted.

- Treat that JSON file as a password. **Never upload or paste it into GitHub, ChatGPT, or a public folder.**
- Keep it outside the repository, e.g. `C:\Users\<your-Windows-user>\.kestrel-private\google-reader.json`.
- Project files ignore common `.env`, credentials folders and local report outputs, but storing secrets outside the repo is safer.
- If key creation is disabled, follow an OAuth/identity-based method instead.

In PowerShell, from your local Kestrel repository:

~~~powershell
python -m pip install -r seo_ops/requirements-optional.txt
$env:GOOGLE_APPLICATION_CREDENTIALS = "$HOME\.kestrel-private\google-reader.json"
python -m seo_ops.google_probe
~~~

Expected **types** of output (actual counts vary and are not provided here):

~~~text
GA4: Data API authentication successful; X daily report rows (...)
GSC: API authentication successful; requested property accessible: YES
GSC: Search Analytics query successful; 0 page rows (...)
Connection check: PASS
~~~

Search Console may return **zero search rows** because fictional pages are intentionally noindex. Zero rows after a successful authenticated request is still a valid API result.

## Part 4. Pull reports to CSV

~~~powershell
python -m seo_ops.cli google-pull --ga4-property 565038230 --gsc-property "https://graceomolola001-cmyk.github.io/kestrel-pseo/" --output-dir reports
~~~

The code creates `reports/ga4-daily.csv` and `reports/gsc-pages.csv`. These CSVs should be treated as private working files, **not** pushed to GitHub.

## Part 5. n8n local (after APIs pass)

n8n supports a Google Service Account credential for HTTP Request nodes. Enable its **Set up for use in HTTP Request node** option and use the same read-only Google API scopes:
- `https://www.googleapis.com/auth/analytics.readonly`
- `https://www.googleapis.com/auth/webmasters.readonly`

The two APIs can be called through HTTP Request nodes:
- POST `https://analyticsdata.googleapis.com/v1beta/properties/565038230:runReport`
- POST `https://www.googleapis.com/webmasters/v3/sites/{URL-ENCODED-KESTREL-GSC-PROPERTY}/searchAnalytics/query`

Add Code/IF nodes to compare counts, label empty responses, and send a summary. Store credentials using **n8n Credentials**, never inline in shared workflow JSON.

## Interview explanation

"This is a real API integration. The Python code authenticates with Google using a restricted identity, queries the GA4 Data API and Search Console API, and exports the responses. It clearly separates actual collected traffic, empty GSC reports, and synthetic fixtures. The n8n workflow uses the same API access to orchestrate reporting and alerts."

## References
- https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart
- https://developers.google.com/webmaster-tools/v1/prereqs
- https://docs.n8n.io/integrations/builtin/credentials/google/service-account/
