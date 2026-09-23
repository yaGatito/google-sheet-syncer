function onChangeTrigger(e) {
  var url = "http://<WEBHOOK-SERVER-URL>/webhook"; 

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var activeCell = sheet.getActiveCell();

  var payload = {
    "sheet_name": sheet.getName(),
    "row": activeCell.getRow(),
    "column": activeCell.getColumn(),
    "value": activeCell.getValue(),
    "timestamp": new Date().toISOString()
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  UrlFetchApp.fetch(url, options);
}
