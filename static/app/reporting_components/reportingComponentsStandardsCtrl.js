angular.module("pathianApp.controllers")
    .controller("reportingComponentsStandardsCtrl", [
        "$scope", "$rootScope", "$location", "$compile", "$http",
        function($scope, $rootScope, $location, $compile, $http) {
            $rootScope.global.linkpath = "#/reporting/components/standards";

            $scope.pdfurl = undefined;
            $scope.exporting = false;

            $scope.nodes = {
                selectedNodes: [],
                selectedPoints: []
            };

            $scope.model = {
                report_year:new Date().getFullYear()
            };

            // entityType is needed to make intensity chart use the right function
            $scope.entityType = 'component';

            $scope.intensityModel = undefined;

            $scope.exportToPdf = function() {
                if ($scope.nodes.selectedNodes.length < 1) {
                    // there are no nodes selected, so don't allow the report
                    alert('You must select at least one component point to report on.');
                    return false;
                }

                if (!$rootScope.global.reportingGroup) {
                    // there is no reporting group selected so don't allow the report
                    alert('You must select a reporting group.');
                    return false;
                }

                $scope.exporting = true;
                var exportingModel = angular.copy($scope.model);
                exportingModel.point_ids = $scope.nodes.selectedNodes.map(function(point) { return point.name });
                exportingModel.submitted_to = $rootScope.global.reportingGroup.id;
                $http.post('/api/ReportingComponents/GetStandardsPDFReport', exportingModel, {responseType: 'arraybuffer'})
                    .success(function(data) {
                        var file = new Blob([data], {type: 'application/pdf'});
                        var fileURL = URL.createObjectURL(file);
                        $scope.pdfurl = fileURL;
                    })
            };

            $scope.openPdf = function() {
                $scope.pdfurl = undefined;
                $scope.exporting = false;
            };

            $scope.treeOptions = {
                template: "#=item.name#",
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/ReportingComponents/PointSelectionTree",
                            dataType: "json"
                        }
                    },
                    schema: {
                        model: {
                            id: "id",
                            hasChildren: "hasChildren"
                        }
                    }
                },
                checkboxes: {
                    template: "# if (item.id.substring(0,6) === 'point:') {# <input type='checkbox' value='true' #= item.checked ? \"checked\" : \"\" # />#}#"
                }
            };

            $scope.submit = function(){
                // reset all models
                $scope.intensityModel = undefined;

                $scope.intensityModel = angular.copy($scope.model);

                // set the point_ids on the model to the selected node ids
                $scope.intensityModel.point_ids = $scope.nodes.selectedNodes.map(function (x) {
                    // return the name of the point as the 'id'
                    return x.name
                });
            };
        }
    ]);