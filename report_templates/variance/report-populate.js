//Report
//loops through data-table data
for(var i = 0;i< window["report_options"].sites.length;i++){
    var site = window["report_options"].sites[i];
    var siteName = site.entity_name;
    $("#data-table").append(
    '<tr class="site">' +
        '<td colspan="19">' + siteName + '</td>' +
    '</tr>'
    );
    for(var j = 0;j< site.sitedata.length;j++){
        var sitedata = site.sitedata[j];
        var dtlabel = sitedata.label;
        var dtjan = sitedata.data[0];
        var dtfeb = sitedata.data[1];
        var dtmar = sitedata.data[2];
        var dtq1 = sitedata.data[3];
        var dtapr = sitedata.data[4];
        var dtmay = sitedata.data[5];
        var dtjun = sitedata.data[6];
        var dtq2 = sitedata.data[7];
        var dtjul = sitedata.data[8];
        var dtaug = sitedata.data[9];
        var dtsep = sitedata.data[10];
        var dtq3 = sitedata.data[11];
        var dtoct = sitedata.data[12];
        var dtnov = sitedata.data[13];
        var dtdec = sitedata.data[14];
        var dtq4 = sitedata.data[15];
        var dtannual = sitedata.data[16];
        var dtnotes = '';

        //If even of odd row
        var rowClass = "even";
        if (j % 2){
            rowClass = "odd";
        }

        //If last row
        if(j == site.sitedata.length-1){
            rowClass = rowClass + " lastrowforsite"
        }

        $("#data-table").append(
            '<tr class="'+ rowClass +'">' +
                '<td>' + dtlabel + '</td>' +
                '<td>' + dtjan + '</td>' +
                '<td>' + dtfeb + '</td>' +
                '<td>' + dtmar + '</td>' +
                '<td>' + dtq1 + '</td>' +
                '<td>' + dtapr + '</td>' +
                '<td>' + dtmay + '</td>' +
                '<td>' + dtjun + '</td>' +
                '<td>' + dtq2 + '</td>' +
                '<td>' + dtjul + '</td>' +
                '<td>' + dtaug + '</td>' +
                '<td>' + dtsep + '</td>' +
                '<td>' + dtq3 + '</td>' +
                '<td>' + dtoct + '</td>' +
                '<td>' + dtnov + '</td>' +
                '<td>' + dtdec + '</td>' +
                '<td>' + dtq4 + '</td>' +
                '<td>' + dtannual + '</td>' +
                '<td>' + dtnotes + '</td>' +
            '</tr>'
        );
    }
}