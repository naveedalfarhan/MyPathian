//Header
var reportyearelements = document.getElementsByClassName("reportyear");
for(var i=0;i < reportyearelements.length;i++){
    reportyearelements[i].innerText = window["report_options"].reportyear;
}

var reportnameelements = document.getElementsByClassName("reportname");
for(var i=0;i < reportnameelements.length;i++){
    reportnameelements[i].innerText = window["report_options"].reportname;
}