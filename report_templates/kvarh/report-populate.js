//Report
for(var i = 0;i< window["report_options"].charts.length;i++)
{
    var chart = window["report_options"].charts[i];
    var entityname = chart.entityname;
    var accountname = chart.accountname;
    var year = chart.year;
    var energyreduction = chart.energyreduction;
    var chart1url = chart.chart1url;
    var chart2url = chart.chart2url;

    $("#reportcontent").append(
        '<div class="div_table_height">'
                + '<div class="info_div">'
                    + '<strong>' + entityname + '</strong>'
                    + '<br>'
                    + accountname
                    + '<br>'
                    + year
                    + '<br>'
                    + 'Energy Reduction: '+ energyreduction + ' kVArh'
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