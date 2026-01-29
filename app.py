function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
  var data = JSON.parse(e.postData.contents);
  
  if (data.action === "clear_all") {
    var lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
    }
    return ContentService.createTextOutput("Cleared");
  } else if (data.action === "delete") {
    var rows = sheet.getDataRange().getValues();
    for (var i = rows.length - 1; i >= 1; i--) {
      if (rows[i][0] == data.Customer && rows[i][1] == data.Number && rows[i][3] == data.Time) {
        sheet.deleteRow(i + 1);
        break; 
      }
    }
    return ContentService.createTextOutput("Deleted");
  } else {
    sheet.appendRow([data.Customer, data.Number, data.Amount, data.Time]);
    return ContentService.createTextOutput("Success");
  }
}
