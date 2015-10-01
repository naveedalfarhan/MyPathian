angular.module("pathianApp.controllers")
    .config(["$compileProvider", function($compileProvider) {
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|blob):/);
    }])
    .controller("reportingGroupsMainCtrl", [
        "$scope", "$rootScope", "$location", "$compile", "$http", "$window", "groupTreeFactory", "groupService", "savedReportConfigurationService",
        function($scope, $rootScope, $location, $compile, $http, $window, groupTreeFactory, groupService, savedReportConfigurationService) {
            $rootScope.global.linkpath = "#/reporting/groups";

            $scope.pdfurl = undefined;
            $scope.exporting = false;

            $scope.nodes = {
                selectedNodes:[],
                forceSelectedNodes:[]
            };
            $scope.energySummaryTableModel = undefined;
            $scope.intensityModel = undefined;
            $scope.totalEnergyModel = undefined;
            $scope.textReportModel = undefined;
            $scope.peakReportModel = undefined;
            $scope.accountChartRows = undefined;

            $scope.model = {
                demand_type:'all',
                comparison_type:'temp',
                account_type:'all',
                start_month:1,
                end_month:12,
                report_year:new Date().getFullYear(),
                benchmark_year:new Date().getFullYear() - 1,
                report_type:"consumption",
                electric_units:"kwh",
                gas_units:'mcf',
                btu_units:'mmbtus',
                submitted_to: undefined,
                selectedGroup: undefined
            };

            $scope.advancedOptions = false;

            $scope.exportToPdf = function() {
                if ($scope.nodes.forceSelectedNodes.length < 1) {
                    // there are no nodes selected, so don't allow the report
                    alert('You must select at least one group to report on.');
                    return false;
                }

                if (!$rootScope.global.reportingGroup) {
                    // there is no reporting group selected so don't allow the report
                    alert('You must select a reporting group.');
                    return false;
                }

                $scope.exporting = true;
                $scope.model.entity_ids = $scope.nodes.forceSelectedNodes.map(function(entry) {return entry.id});
                $scope.model.submitted_to = $rootScope.global.reportingGroup.id;
                $http.post('/api/ReportingGroups/GetReport', $scope.model, {responseType: 'arraybuffer'})
                    .success(function(data) {
                        var file = new Blob([data], {type: 'application/pdf'});
                        var fileURL = URL.createObjectURL(file);
                        $scope.pdfurl = fileURL;
                });
            };

            $scope.openPdf = function() {
                $scope.pdfurl = undefined;
                $scope.exporting = false;
            };

            $scope.$watchCollection("nodes.selectedNodes", function() {
                if ($scope.nodes.selectedNodes.length == 1) {
                    $http.get("/api/groups/getChildrenOf?id=" + $scope.nodes.selectedNodes[0].id)
                        .then(function (d) {
                            $scope.nodes.forceSelectedNodes = d.data.length ? d.data : $scope.nodes.selectedNodes.slice(0);
                        })
                } else {
                    $scope.nodes.forceSelectedNodes = $scope.nodes.selectedNodes.slice(0);
                }
            });

            $scope.$watch('model.selectedGroup', function(){
                // if the selected group is undefined, set it, which will call this function again
                if (!$scope.model.selectedGroup) {
                    if ($scope.reportNodes.length > 0)
                        $scope.model.selectedGroup = $scope.reportNodes[0].id;
                }
                else if ($scope.groupChangeFunction != undefined && $scope.groupChangeFunction != null) { // now that the selected group has been set, run the chart generation
                    $scope.groupChangeFunction();
                }
            });

            $scope.accountChartRows = [];

            $scope.createConsumptionCharts = function(){
                var group_id = $scope.model.selectedGroup;

                $scope.consumptionModels = [];
                $scope.accountChartRows = [];

                if ($scope.model.report_type === "consumption"){
                    $scope.totalEnergyModel = angular.copy($scope.model);
                    $scope.totalEnergyModel.entity_ids = [group_id];
                }

                groupService.getAccounts({id:group_id}, function(accounts) {
                    for (var j=0; j < accounts.length; ++j){
                        if ($scope.model.account_type !== 'all' && $scope.model.account_type !== accounts[j].type)
                            continue;
                        if (($scope.model.report_type === 'kvar' || $scope.model.report_type === 'kva' || $scope.model.report_type === 'powerfactor') && accounts[j].type.toLowerCase() !== 'electric')
                            continue;

                        var consumptionModel = angular.copy($scope.model);
                        consumptionModel.entity_ids = [group_id];
                        consumptionModel.account_type = accounts[j].type;


                        $scope.accountChartRows.push({
                            name: accounts[j].name,
                            model: consumptionModel
                        });
                    }
                });
            };

            $scope.model.selectedGroup = "";

            $scope.reportNodes = [];

            $scope.createPeakReport = function() {
                $scope.peakReportModel = angular.copy($scope.model);
                $scope.peakReportModel.entity_ids = [$scope.model.selectedGroup];
            };

            $scope.submit = function(){
                // reset all reporting models
                $scope.energySummaryTableModel = undefined;
                $scope.intensityModel = undefined;
                $scope.peakReportModel = undefined;
                $scope.textReportModel = undefined;
                $scope.totalEnergyModel = undefined;
                $scope.accountChartRows = [];

                if ($scope.nodes.forceSelectedNodes.length < 1){
                    alert("You must select at least one group to report on.");
                    return false;
                }

                $scope.reportNodes = $scope.nodes.forceSelectedNodes;

                if ($scope.model.report_type === 'text'){
                    $scope.textReportModel = angular.copy($scope.model);
                    $scope.textReportModel.entity_ids = $scope.reportNodes.map(function (node) {
                        return node.id
                    });
                    $scope.groupChangeFunction = undefined;
                    $scope.model.selectedGroup = undefined
                }
                else if ($scope.model.report_type === 'peak') {
                    $scope.groupChangeFunction = $scope.createPeakReport;
                    $scope.model.selectedGroup = undefined;
                }
                else{
                    if ($scope.model.report_type === "consumption"){
                        $scope.model.entity_ids = $scope.reportNodes.map(function(record) { return record.id });
                        $scope.intensityModel = angular.copy($scope.model);
                        $scope.energySummaryTableModel = angular.copy($scope.model);
                    }

                    $scope.groupChangeFunction = $scope.createConsumptionCharts;
                    $scope.model.selectedGroup = undefined;
                }
            };

            $scope.treeOptions = {
                dataTextField: "name",
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/groups/getChildrenOf",
                            dataType: "json"
                        }
                    },
                    schema: {
                        model: {
                            id: "id",
                            hasChildren: "childIds.length > 0"
                        }
                    }
                },
                checkboxes:{children:false}
            };

            var queryParams = $location.search();
            if (queryParams.report_id) {
                // send from the dashboard for a quick report, so get the report and run it.
                $scope.quickReport = true;
                savedReportConfigurationService.getConfigurationById({id:queryParams.report_id}, function(data) {
                    $scope.nodes.selectedNodes = data.config.entity_ids;
                    $scope.model = data.config.configuration;
                    $scope.selectedConfig = queryParams.report_id;
                    $scope.exporting = true;
                    var reportModel = angular.copy(data.config.configuration);
                    if (data.config.entity_ids.length == 1) {
                        $http.get("/api/groups/getChildrenOf?id=" + data.config.entity_ids[0].id)
                            .then(function (d) {
                                reportModel.entity_ids = d.data.length ? d.data : data.config.entity_ids.slice(0);
                                reportModel.entity_ids = reportModel.entity_ids.map(function(entry) {return entry.id});
                                reportModel.submitted_to = $rootScope.global.reportingGroup.id;
                                $http.post('/api/ReportingGroups/GetReport', reportModel, {responseType: 'arraybuffer'})
                                    .success(function(data) {
                                        var file = new Blob([data], {type: 'application/pdf'});
                                        var fileURL = URL.createObjectURL(file);
                                        $scope.pdfurl = fileURL;
                                });
                            })
                    } else {
                        reportModel.entity_ids = data.config.entity_ids.slice(0);
                        reportModel.entity_ids = reportModel.entity_ids.map(function(entry) {return entry.id});
                        reportModel.submitted_to = $rootScope.global.reportingGroup.id;
                        $http.post('/api/ReportingGroups/GetReport', reportModel, {responseType: 'arraybuffer'})
                            .success(function(data) {
                                var file = new Blob([data], {type: 'application/pdf'});
                                var fileURL = URL.createObjectURL(file);
                                $scope.pdfurl = fileURL;
                    });
                    }

                });
            }
        }
    ]);