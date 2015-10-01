//loops through data-table data
var rowClass = "";
window["report_options"].differencetable.forEach(function(row){
    $("#differencetable").append("<tr class='" + rowClass + "'>" +
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

//This is expecting an array called charts. Each array position will contain the required datapoints for a set separated by a semicolon
for(var i = 0;i< window["report_options"].charts.length;i++){
    var component = window["report_options"].charts[i].component_description;
    var chart1url = window["report_options"].charts[i].chart1url;
    var chart2url = window["report_options"].charts[i].chart2url;

    $("#reportcontent").append(
        '<div class="div_table_height">'
                + '<div class="info_div">'
                    + '<strong>' + component + '</strong>'
                + '</div>'
                + '<div class="chart_div">'
                    + '<img src="' + chart1url + '" width="350"/>'
                + '</div>'
                + '<div class="chart_div">'
                    + '<img src="' + chart2url + '" width="350"/>'
                + '</div>'
                + '<div style="clear:both"></div>'
        + '</div>'
    );
}