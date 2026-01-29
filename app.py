function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
  var data = JSON.parse(e.postData.contents);
  
  // စာရင်းအားလုံးကို တစ်ခါတည်း ဖျက်ရန်
  if (data.action === "clear_all") {
    var lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
    }
    return ContentService.createTextOutput("Cleared");
  } 
  
  // ပုံမှန် စာရင်းသွင်းရန်
  else {
    sheet.appendRow([data.Customer, data.Number, data.Amount, data.Time]);
    return ContentService.createTextOutput("Success");
  }
}
