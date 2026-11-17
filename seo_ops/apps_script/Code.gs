/**
 * Kestrel SEO Ops -> Google Sheets, with deduplicated error alerts.
 * Bound script or standalone Apps Script. Configure script properties:
 * SPREADSHEET_ID, REPORT_URL, ALERT_EMAIL (optional).
 * Calls only a public report URL; does not need GitHub credentials.
 */
function syncSeoHealth() {
  const properties = PropertiesService.getScriptProperties();
  const spreadsheetId = properties.getProperty('SPREADSHEET_ID');
  const reportUrl = properties.getProperty('REPORT_URL');
  const email = properties.getProperty('ALERT_EMAIL');
  if (!spreadsheetId || !reportUrl || !/^https:\/\//.test(reportUrl)) {
    throw new Error('Configure SPREADSHEET_ID and HTTPS REPORT_URL in Script Properties');
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const response = UrlFetchApp.fetch(reportUrl, {muteHttpExceptions:true, followRedirects:true});
    if (response.getResponseCode() !== 200) throw new Error('Report fetch failed: ' + response.getResponseCode());
    const report = JSON.parse(response.getContentText());
    if (report.schema_version !== 1 || !Array.isArray(report.findings)) throw new Error('Unexpected report format');
    const book = SpreadsheetApp.openById(spreadsheetId);
    const sheet = book.getSheetByName('SEO Health') || book.insertSheet('SEO Health');
    sheet.clearContents();
    sheet.getRange(1,1,1,7).setValues([['Run (UTC)','Mode','Status','Severity','Code','Page','Detail']]);
    const rows = report.findings.map(f => [report.created_at, report.mode, report.status, f.severity, f.code, f.url, f.detail]);
    if (!rows.length) rows.push([report.created_at,report.mode,report.status,'INFO','NO_FINDINGS',report.target,'Review audit coverage']);
    sheet.getRange(2,1,rows.length,7).setValues(rows);
    sheet.setFrozenRows(1);
    // Alert once per unique set of failures, even if the report timestamp changes.
    const fingerprint = report.findings.filter(f => f.severity === 'error')
      .map(f => [f.code, f.url, f.detail].join('|')).sort().join('\n');
    const digest = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, fingerprint));
    if (fingerprint && digest !== properties.getProperty('LAST_ALERT_DIGEST') && email) {
      MailApp.sendEmail(email, 'SEO Ops: ' + report.counts.error + ' error(s)',
        'New SEO errors detected. Review the SEO Health tab: ' + book.getUrl());
    }
    properties.setProperty('LAST_ALERT_DIGEST', digest);
    properties.setProperty('LAST_REPORT_SYNC', report.created_at);
  } finally {
    lock.releaseLock();
  }
}

function installDailyTrigger() {
  const exists = ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'syncSeoHealth');
  if (!exists) ScriptApp.newTrigger('syncSeoHealth').timeBased().everyDays(1).atHour(9).create();
}
