//Header
var reportnameelements = document.getElementsByClassName("reportname");
for(var i=0;i < reportnameelements.length;i++){
    reportnameelements[i].innerText = window["report_options"].reportname;
}