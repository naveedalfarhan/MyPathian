//Footer
var reportdateelements = document.getElementsByClassName("reportdate");

for(var i=0;i < reportdateelements.length;i++){
    reportdateelements[i].innerText = window["report_options"].reportdate;
}