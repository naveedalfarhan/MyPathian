angular.module("pathianApp.controllers")
    .controller("bronzeReportingIndexCtrl", [
        "$scope", "$rootScope",
        function($scope, $rootScope){
            $rootScope.global.linkpath = "#/bronze";
        }
    ]);