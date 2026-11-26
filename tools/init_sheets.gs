/**
 * dedek-youtube — one-time spreadsheet setup (STANDALONE Apps Script).
 *
 * How to use:
 *   1. Go to https://script.google.com -> New project.
 *   2. Replace the contents of Code.gs with this whole file. Save.
 *   3. Select function `initDedekSheets` and click Run.
 *   4. Accept the authorization prompt (Sheets + Drive).
 *   5. Open the Execution log to see what happened.
 *
 * Idempotent: safe to run again. Only creates missing tabs and writes a
 * missing/empty header row. Existing data is never touched.
 */

// The spreadsheet this project uses.
var SHEET_ID = '1OTAoHRg0ijCUS9YdZG2Vl8a4WsaadiwAnLHko3LWEJ8';

var DEDEK_SHEETS = {
  Video: ['url'],
  Channel: ['url'],
  Exclude: ['video_id'],
  Combined: [
    'video_id', 'video_url', 'title', 'channel_id',
    'channel_name', 'source', 'published_at', 'updated_at'
  ]
};

function initDedekSheets() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var log = ['spreadsheet: ' + ss.getName() + ' (' + SHEET_ID + ')'];

  Object.keys(DEDEK_SHEETS).forEach(function (name) {
    var header = DEDEK_SHEETS[name];
    var sh = ss.getSheetByName(name);
    if (!sh) {
      sh = ss.insertSheet(name);
      log.push('created tab: ' + name);
    } else {
      log.push('found tab:   ' + name);
    }

    var first = sh.getRange(1, 1, 1, header.length).getValues()[0];
    var isEmpty = first.every(function (v) { return String(v).trim() === ''; });
    var matches = JSON.stringify(first.map(String)) === JSON.stringify(header);

    if (isEmpty || !matches) {
      sh.getRange(1, 1, 1, header.length).setValues([header]);
      sh.setFrozenRows(1);
      log.push('  header written: ' + header.join(', '));
    } else {
      log.push('  header ok');
    }
    sh.setColumnWidth(1, 220);
  });

  // Remove the default empty "Sheet1" if it is not one we use.
  var def = ss.getSheetByName('Sheet1');
  if (def && ss.getSheets().length > 1 && def.getLastRow() === 0) {
    ss.deleteSheet(def);
    log.push('removed empty default Sheet1');
  }

  // The app fetches Combined as CSV without auth, so the file must be public.
  try {
    DriveApp.getFileById(SHEET_ID)
      .setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    log.push('sharing set: anyone-with-link = viewer');
  } catch (e) {
    log.push('sharing NOT set (' + e + ') — set it manually: Share -> Anyone with the link -> Viewer');
  }

  if (ss.getSheetByName('Video')) ss.setActiveSheet(ss.getSheetByName('Video'));

  Logger.log(log.join('\n'));
}
