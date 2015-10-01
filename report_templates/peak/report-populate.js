//Report

//loops through data-table data
for(var i = 0;i < window["report_options"].sets.length;i++){
    var item = window["report_options"].sets[i];
    var dtlocation = item.location;
    var dtdate = item.date;
    var dtchart1 = item.chart1;
    var dtchart2 = item.chart2;
    var dtdatatable = item.datatable;
    $("#report").append(
        '<div class="report-container">' +
            '<table class="data-table">' +
                '<tr class="table-info">' +
                    '<td>' +
                        '<p>' + dtlocation + '</p>' +
                        '<p>' + dtdate + '</p>' +
                    '</td>' +
                '<tr>' +
                '<tr>'+
                    '<td><img src="' + dtchart1 + '" width="750" /></td>' +
                '</tr>' +
                '<tr>'+
                    '<td><img src="' + dtchart2 + '" width="750" /></td>' +
                '</tr>' +
                '<tr>'+
                    '<td class="inner-data-table-container"><table class="inner-data-table" id="dt'+ i + '"><tr><th>Year</th><th>kW</th><th>Date</th></tr></table></td>' +
                '</tr>' +
            '</table>' +
        '</div>'
    );
    for(var j = 0;j < dtdatatable.length;j++){
        if (j == 0) {
            var datatableobject =  dtdatatable[j];
            var dtyear = datatableobject.year;
            var dtkw = datatableobject.kw;
            var dtdate = datatableobject.date;
            $("#dt" + i).append(
                '<tr id="toRemove">'+
                    '<td>' + dtyear + '</td>' +
                    '<td>' + dtkw + '</td>' +
                    '<td>' + dtdate + '</td>' +
                '</tr>'
            );
        }

        $("#toRemove").remove();

        var datatableobject =  dtdatatable[j];
        var dtyear = datatableobject.year;
        var dtkw = datatableobject.kw;
        var dtdate = datatableobject.date;
        $("#dt" + i).append(
            '<tr>'+
                '<td>' + dtyear + '</td>' +
                '<td>' + dtkw + '</td>' +
                '<td>' + dtdate + '</td>' +
            '</tr>'
        );
    }
}