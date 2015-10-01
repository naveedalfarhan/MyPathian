//Report
$(".AvgUnitReduction").text(window["report_options"].AvgUnitReduction);
$(".AvgCostReduction").text(window["report_options"].AvgCostReduction);
$(".Units").text(window["report_options"].Units);
$("#intensitychart").attr("src", window["report_options"].intensitychartsrc);


//loops through data-table data
for(var i = 0;i< window["report_options"].datatable.length;i++){
    var dtentity = window["report_options"].datatable[i].entity;
    var dtutility = window["report_options"].datatable[i].utility;
    var dtreported = window["report_options"].datatable[i].reported;
    var dtbenchmark = window["report_options"].datatable[i].benchmark;
    var dtdifference = window["report_options"].datatable[i].difference;
    var dtchange = window["report_options"].datatable[i].change;
    var dtsavings = window["report_options"].datatable[i].savings;
    var dttype = window["report_options"].datatable[i].type;
    $("#data-table").append(
        '<tr class="'+ dttype +'">' +
            '<td>' + dtentity + '</td>' +
            '<td>' + dtutility + '</td>' +
            '<td>' + dtreported + '</td>' +
            '<td>' + dtbenchmark + '</td>' +
            '<td>' + dtdifference + '</td>' +
            '<td>' + dtchange + '</td>' +
            '<td>' + dtsavings + '</td>' +
        '</tr>'
    )
}

//This is expecting an array called charts. Each array position will contain the required datapoints for a set separated by a semicolon
for(var i = 0;i< window["report_options"].charts.length;i++){
    var val1 = window["report_options"].charts[i].entityname;
    var val2 = window["report_options"].charts[i].accountname;
    var year = window["report_options"].charts[i].year;
    var energyreduction = window["report_options"].charts[i].energyreduction;
    var costreduction = window["report_options"].charts[i].costreduction;
    var chartscalculatedat = window["report_options"].charts[i].chartscalculatedat;
    var chart1url = window["report_options"].charts[i].chart1url;
    var chart2url = window["report_options"].charts[i].chart2url;

    $("#reportcontent").append(
        '<div class="div_table_height">'
                + '<div class="info_div">'
                    + '<strong>' + val1 + ' (' + year + ')' + '</strong>'
                    + '<br>'
                    + val2
                    + '<br>'
                    + 'Energy Reduction: ' + energyreduction
                    + '<br>'
                    + 'Cost Reduction: ' + costreduction
                    + '<br>'
                    + '(calculated at:' + chartscalculatedat + ')'
                + '</div>'
                + '<div class="chart_div">'
                    + '<img src="' + chart1url + '" width="350"/>'
                + '</div>'
                + '<div class="chart_div">'
                    + '<img src="' + chart2url + '" width="350"/>'
                + '</div>'
                + '<div style="clear:both"></div>'
            + '</div>'
        + '</div>'
    );
}