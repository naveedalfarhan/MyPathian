//Cover fields
var reportdateelements = document.getElementsByClassName("reportdate");
for(var i=0;i < reportdateelements.length;i++){
    reportdateelements[i].innerText = window["report_options"].reportdate;
}

var reportnameelements = document.getElementsByClassName("reportname");
for(var i=0;i < reportnameelements.length;i++){
    reportnameelements[i].innerText = window["report_options"].reportname;
}

var submittedtoelements = document.getElementsByClassName("submittedto");
for(var i=0;i < submittedtoelements.length;i++){
    submittedtoelements[i].innerText = window["report_options"].submittedto;
}

var submittedbyelements = document.getElementsByClassName("submittedby");
for(var i=0;i < submittedbyelements.length;i++){
    submittedbyelements[i].innerText = window["report_options"].submittedby;
}