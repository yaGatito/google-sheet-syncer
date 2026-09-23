function onChangeTrigger(e) {
  var url = "http://<WEBHOOK-SERVER-URL>/webhook"; 

  if (!e) {
    Logger.log("Event object is undefined. Run this by making a change in the sheet.");
    return;
  }

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var activeCell = sheet.getActiveCell();

  var payload = {
    "sheet_name": sheet.getName(),
    "row": activeCell.getRow(),
    "column": activeCell.getColumn(),
    "value": activeCell.getValue(),
    "change_type": e.changeType || "EDIT", 
    "timestamp": new Date().toISOString()
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  UrlFetchApp.fetch(url, options);
}
