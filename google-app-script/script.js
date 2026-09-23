function getConfig() {
  var properties = PropertiesService.getScriptProperties();

  return {
    url: properties.getProperty("WEBHOOK_URL"),
    secret: properties.getProperty("WEBHOOK_SECRET")
  };
}

function onChangeTrigger(e) {
  var config = getConfig();

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var row = sheet.getActiveCell().getRow();

  if (row <= 1) return;

  var rowValues = sheet.getRange(row, 1, 1, 5).getValues()[0];

  // Validation
  if (!rowValues[0] || !rowValues[1] || !rowValues[2] || !rowValues[3] || !rowValues[4]) return;

  var payload = {
    "id": row - 1,
    "name": rowValues[0] ? rowValues[0].toString() : "",
    "desc": rowValues[1] ? rowValues[1].toString() : "",
    "type": rowValues[2] ? rowValues[2].toString() : "",
    "amount": rowValues[3] !== "" ? parseInt(rowValues[3]) : 0,
    "extra": rowValues[4] ? rowValues[4].toString() : "",
  };

  var options = {
    "method": "post",
    "headers": {
      "X-Webhook-Secret": config.secret
    },
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  UrlFetchApp.fetch(config.url, options);
}
