/**
 * Created by badams on 9/23/2014.
 */

angular.module("pathianApp.controllers")
    .controller("reportingComponentsComparisonCtrl", ["$scope", "$rootScope", "$location", "$http",
        function($scope, $rootScope, $location, $http) {
            $rootScope.global.linkpath = "#/reporting/components/comparisons";

            $scope.pdfurl = undefined;
            $scope.exporting = false;

            $scope.nodes = {
                selectedNodes: []
            };

            $scope.model = {
                start_month:1,
                end_month:12,
                comparison_year:new Date().getFullYear(),
                historical_mode:false,
                historical_years:[],
                unit: 'mmbtu'
            };

            $scope.possible_years = [];
            for (var year=2005; year <= new Date().getFullYear() - 1; ++year) {
                $scope.possible_years.push(year);
            }

            // reverse list of years
            $scope.possible_years = $scope.possible_years.sort(function(a,b) { return b-a });

            // entityType is needed to make intensity chart use the right function
            $scope.entityType = 'component';

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
                exportingModel.component_ids = $scope.nodes.selectedNodes.map(function(point) { return point.id });
                exportingModel.submitted_to = $rootScope.global.reportingGroup.id;
                $http.post('/api/ReportingComponents/GetComparisonPDFReport', exportingModel, {responseType: 'arraybuffer'})
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
                            url: "/api/ReportingComponents/ReportingTree",
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
                checkboxes: true
            };

            $scope.submit = function(){
                if ($scope.nodes.selectedNodes.length <= 0) {
                    alert("You must select components to report on.");
                    return false;
                }

                if (!$rootScope.global.reportingGroup) {
                    // there is no reporting group selected so don't allow the report
                    alert('You must select a reporting group.');
                    return false;
                }

                // reset chart model
                $scope.chartModel = angular.copy($scope.model);
                $scope.chartModel.component_ids = $scope.nodes.selectedNodes.map(function(x) {
                    return x.id;
                });
                $scope.chartModel.submitted_to = $rootScope.global.reportingGroup.id;

                // set table model
                $scope.tableModel = angular.copy($scope.chartModel);
            };
        }
    ]);