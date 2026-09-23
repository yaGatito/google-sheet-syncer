const url = "http://tidy-worsening-womanless.ngrok-free.dev/webhook";

function onChangeTrigger(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var row = sheet.getActiveCell().getRow();

  if (row <= 1) return;

  var rowValues = sheet.getRange(row, 1, 1, 5).getValues()[0];

  // Validation
  if (!rowValues[0] || !rowValues[1] || !rowValues[2] || !rowValues[3] || !rowValues[4]) return;

  var payload = {
    "change_type": "EDIT",
    "id": row,
    "name": rowValues[0] ? rowValues[0].toString() : "",
    "desc": rowValues[1] ? rowValues[1].toString() : "",
    "type": rowValues[2] ? rowValues[2].toString() : "",
    "amount": rowValues[3] !== "" ? parseInt(rowValues[3]) : 0,
    "extra": rowValues[4] ? rowValues[4].toString() : "",
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  UrlFetchApp.fetch(url, options);
}
