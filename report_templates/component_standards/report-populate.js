//Report
$("#standardschart").attr("src", window["report_options"].standardschartsrc);

// add table data
var $table = $("#standardstable");
var rowClass = "";
window["report_options"].standardstable.forEach(function(row) {
    $table.append("<tr class='" + rowClass + "'><td>" + row.component + "</td><td>" + row.description + "</td><td>" +
        row.units + "</td><td>" + row.ppsn + "</td><td>" + row.bic + "</td><td>" + row.diff + "</td></tr>");
    if (rowClass === "")
        rowClass = "alt";
    else
        rowClass = "";
});