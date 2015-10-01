angular.module("pathianApp.controllers")
    .controller("reportingEquipmentSyrxCtrl", [
        "$scope", "$rootScope", "$location", "$compile", "$http",
        function($scope, $rootScope, $location, $compile, $http) {
            $rootScope.global.linkpath = "#/reporting/syrx";
            $scope.selectedEquipment = [];
            $scope.exporting = false;
            $scope.pdfurl = null;

            $scope.runReport = function() {
                $scope.exporting = true;
                var equipmentIds = $scope.selectedEquipment.map(function(x) { return x.id; });
                var postData = {
                    "equipment_ids": equipmentIds,
                    "submitted_to": $rootScope.global.reportingGroup.id
                };
                $http.post('/api/ReportingEquipment/ParagraphReport', postData, {responseType: 'arraybuffer'})
                    .success(function(data) {
                        var file = new Blob([data], {type: 'application/pdf'});
                        var fileURL = URL.createObjectURL(file);
                        $scope.pdfurl = fileURL;
                });
            };

            $scope.openPdf = function() {
                $scope.pdfurl = null;
                $scope.exporting = false;
            };
        }
    ]);