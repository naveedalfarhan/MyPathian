//Report
$("#comparisonchart").attr("src", window["report_options"].comparisonchartsrc);

// add table data
var $table = $("#comparisontable");
var rowClass = "";
window["report_options"].comparisontable.forEach(function(row) {
    $table.append("<tr class='" + rowClass + "'>" +
        "<td>" + row.equipment_name + "</td>" +
        "<td>" + row.component_id + "</td>" +
        "<td>" + row.description + "</td>" +
        "<td>" + row.units + "</td>" +
        "<td>" + row.diff + "</td>" +
        "<td>" + row.hour_diff + "</td>" +
        "<td>" + row.year_diff + "</td>" +
        "<td>" + row.hour_cost_diff + "</td>" +
        "<td>" + row.year_cost_diff + "</td>" +
        "</tr>");
    if (rowClass === "")
        rowClass = "alt";
    else
        rowClass = "";
});