# Connect Kestrel to GA4 and Google Search Console

Kestrel is a **fictional, intentionally noindex** SEO engineering demonstration. It uses genuine site instrumentation and can make real Google API calls after authorized setup. No fabricated metrics should be presented as genuine search traffic.

## A. Add the Google Analytics 4 website tag

1. Visit https://analytics.google.com/ and create (or select) a GA4 property named **Kestrel SEO Lab**.
2. Under **Admin → Data streams**, create a **Web** stream for:
   https://graceomolola001-cmyk.github.io/kestrel-pseo/
3. Copy the **Measurement ID** (begins with G-). This identifies the web stream and is **not** the numeric GA4 property ID.
4. **Current Kestrel default:** the deployment workflow includes the public web Measurement ID `G-K3E3Z1C089`. The numeric GA4 property ID supplied for API reporting is `565038230` (the latter is not a browser tracking tag).
5. The default is used when no repository variable named `KESTREL_GA4_MEASUREMENT_ID` is set. If that variable already exists, it takes priority, so check it if the website shows another measurement ID.
6. Open **Actions → Check, build and deploy** to confirm the release deployed. New deployments add Google's normal `gtag.js` snippet to generated pages.
7. View page source and search for `G-K3E3Z1C089` to confirm installation. Visit the site, then check **GA4 → Reports → Realtime** or DebugView for incoming events.

**Do not** add the GA4 measurement ID as a service account key or OAuth client secret. It is a public browser-side ID and can be stored as a GitHub Actions variable.

**Privacy and consent:** Before using this setup with genuine users, assess applicable privacy notices and consent requirements. This fictional demonstration does not collect admissions applications or student records.

## B. Verify the Search Console URL-prefix property

1. Visit https://search.google.com/search-console and add a **URL-prefix** property:
   https://graceomolola001-cmyk.github.io/kestrel-pseo/
2. Choose the **HTML tag** ownership verification method.
3. Google supplies something similar to:
   <meta name="google-site-verification" content="EXAMPLE_TOKEN_FROM_GOOGLE">
4. Copy **only the content attribute value**, not the whole meta element.
5. In **GitHub → Settings → Secrets and variables → Actions → Variables**, add:
   - Name: KESTREL_GSC_VERIFICATION_TOKEN
   - Value: the exact verification content token
6. Redeploy by running **Check, build and deploy** on main.
7. Open the published site's **View Page Source** and verify that the meta tag is present. Then return to Search Console and click **Verify**.

Because this is hosted under the github.io domain, use the exact project URL prefix. You do not control the parent github.io DNS domain.

The pages deliberately remain **noindex**; Search Console can verify ownership without the site being eligible for indexing. Zero search clicks or impressions is a valid response for this demonstration.

## C. What happens in the code

- build.py reads the two **optional** environment variables.
- It validates the expected G- measurement ID and GSC verification-token format.
- It emits the GA4 gtag.js loader and/or Google verification meta tag into the HTML head.
- The deployed build defaults to `G-K3E3Z1C089` if the optional GA4 repository variable is absent. Local builds without configuration still do not inject Google tracking.
- The automated tests verify both the no-credentials and configured paths.
- GitHub Actions passes the configured repository variable, if supplied, or the current public default Measurement ID. The tag is included in the published pages after successful deployment.

## D. Connecting the reporting APIs is a different step

A G- measurement ID identifies a website data stream. It does **not** authenticate an API request.

The existing seo_ops/google_data.py module uses *read-only* Google OAuth scopes and supports:
- GA4 Data API: daily sessions and key-event metrics.
- Search Console Search Analytics API: clicks, impressions, CTR and average position by page.

These requests additionally require:
1. An authorized Google Cloud project with both APIs enabled.
2. A permitted OAuth user or service-account identity with access to the relevant Google properties.
3. The **numeric GA4 Property ID**, which differs from G-.
4. The exact Search Console property identifier, here the full URL-prefix property.
5. Valid credentials stored outside GitHub and never pasted into chat or published source code.

The API may return empty Search Console results for a new, noindex demonstration. Never substitute synthetic metrics without clearly identifying them.

## Official instructions

- GA4 website setup: https://support.google.com/analytics/answer/14183469
- Search Console verification: https://support.google.com/webmasters/answer/9008080
- Google Analytics Data API: https://developers.google.com/analytics/devguides/reporting/data/v1
- Search Console API: https://developers.google.com/webmaster-tools/v1/api_reference_index
