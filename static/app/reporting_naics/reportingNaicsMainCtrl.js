angular.module("pathianApp.controllers")
    .controller("reportingNaicsMainCtrl", [
        "$scope", "$rootScope", "$location", "$compile", "$http", "reportingNaicsService", "groupService", "savedReportConfigurationService",
        function($scope, $rootScope, $location, $compile, $http, reportingNaicsService, groupService, savedReportConfigurationService) {
            $rootScope.global.linkpath = "#/reporting/naics";

            $scope.nodes = {
                selectedNodes:[],
                forceSelectedNodes:[]
            };

            $scope.model = {
                demand_type:'all',
                comparison_type:'temp',
                account_type:'all',
                start_month:1,
                end_month:12,
                report_year:2014,
                benchmark_year:2013,
                report_type:"consumption",
                electric_units:"kwh",
                gas_units:'mcf',
                btu_units:'mmbtus',
                selectedNaics: '',
                selectedGroup: ''
            };

            $scope.advancedOptions = false;


            function resetGroups() {
                $scope.naicsGroups = [];
                $scope.model.selectedGroup = '';
            }

            resetGroups();

            $scope.naicsTotalEnergyModel = undefined;
            $scope.groupTotalEnergyModel = undefined;
            $scope.accountChartRows = [];
            $scope.entityType = "naics";

            $scope.naicsNodes = [];
            $scope.groupsNodes = [];
            $scope.reportNodes = [];

            $scope.naicsChangeFunction = undefined;

            $scope.exporting = false;

            $scope.exportToPdf = function(){
                if ($scope.nodes.forceSelectedNodes.length < 1) {
                    // there are no nodes selected, so don't allow the report
                    alert('You must select at least one group or NAICS code to report on.');
                    return false;
                }

                if (!$rootScope.global.reportingGroup) {
                    // there is no reporting group selected so don't allow the report
                    alert('You must select a reporting group.');
                    return false;
                }

                $scope.reportNodes = $scope.nodes.forceSelectedNodes;

                var postUrl = '';

                // check to see if the report is on NAICS codes or groups
                if ($scope.reportNodes[0].id.substr(0, 2) === 'g_') { // groups
                    $scope.entityType = 'group';
                    postUrl = '/api/ReportingGroups/GetReport';
                } else { // naics
                    $scope.entityType = 'naics';
                    postUrl = '/api/ReportingNaics/GetReport';
                }

                // sort the report nodes alphanumerically by specifying the comparison operator for sorting
                // for more information http://www.javascriptkit.com/javatutors/arraysort2.shtml
                $scope.reportNodes = $scope.reportNodes.sort(function(a, b) {
                    var aName = a.name.toLowerCase(), bName = b.name.toLowerCase();
                    if (aName < bName) { return -1; }
                    if (aName > bName) { return 1; }
                    return 0;
                });

                // remove the prefix of all the id's since we know the entityType now
                $scope.reportNodes = $scope.reportNodes.map(function (node) {
                    return {'id': node.id.substring(2), 'childIds': node.childIds, 'name': node.name }
                });

                $scope.exporting = true;
                $scope.model.entity_ids = $scope.reportNodes.map(function(entry) {return entry.id});
                $scope.model.submitted_to = $rootScope.global.reportingGroup.id;
                $http.post(postUrl, $scope.model, {responseType: 'arraybuffer'})
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
                    $http.get("/api/Naics/getChildrenOf?id=" + $scope.nodes.selectedNodes[0].id + "&restrict_type=true")
                        .then(function (d) {
                            $scope.nodes.forceSelectedNodes = d.data.length ? d.data : $scope.nodes.selectedNodes.slice(0);
                        })
                } else {
                    if ($scope.nodes.selectedNodes.length > 0) {
                        var samePrefix = true;
                        // get the first prefix
                        var firstPrefix = $scope.nodes.selectedNodes[0].id.substring(0,2);
                        // check each node and ensure they have the same prefix
                        for (var i=0; i < $scope.nodes.selectedNodes.length; ++i) {
                            // if the node isn't the same as the first, break the loop and set samePrefix to false
                            if ($scope.nodes.selectedNodes[i].id.substring(0,2) !== firstPrefix) {
                                // not the same, so the report cannot be run
                                samePrefix = false;
                                break;
                            }
                        }

                        if (samePrefix)
                            $scope.nodes.forceSelectedNodes = $scope.nodes.selectedNodes.slice(0);
                        else
                            $scope.nodes.forceSelectedNodes = [];
                    } else {
                        $scope.nodes.forceSelectedNodes = [];
                    }
                }
            });


            // watch for the naics code to change, as it changing needs to cause the groups dropdown to repopulate
            $scope.$watch('model.selectedNaics', function(){
                if (!$scope.model.selectedNaics) {
                    if ($scope.reportNodes.length > 0 && $scope.entityType === 'naics')
                        $scope.model.selectedNaics = $scope.reportNodes[0].id;
                    return false;
                }
                // if there is a function to be ran when the naics code is changed, run it
                if ($scope.naicsChangeFunction != undefined && $scope.naicsChangeFunction != null) {
                    $scope.naicsChangeFunction();
                }
                // if the text or peak report models are both null, find the naicsGroups
                if (!$scope.textReportModel && !$scope.peakReportModel) {
                    reportingNaicsService.getGroups({code: $scope.model.selectedNaics}, function (data) {
                        if (data.length > 0) {
                            $scope.naicsGroups = data;
                            $scope.model.selectedGroup = data[0].id;
                        }
                        else { // there are no groups for the naics code so don't show anything
                            resetGroups();
                        }
                    });
                }
            });

            // watch for the selected group to change, as it will need to regenerate the charts
            $scope.$watch('model.selectedGroup', function() {
                // if the selected group is undefined, set it, which will call this function again
                if (!$scope.model.selectedGroup) {
                    if ($scope.naicsGroups.length > 0)
                        $scope.model.selectedGroup = $scope.naicsGroups[0].id;
                    return false;
                }
                // if the group change function is defined, run it
                else if ($scope.groupChangeFunction != undefined && $scope.groupChangeFunction != null) {
                    $scope.groupChangeFunction();
                }
            });

            $scope.createPeakReport = function() {
                $scope.peakReportModel = angular.copy($scope.model);
                if ($scope.entityType === 'naics')
                    $scope.peakReportModel.entity_ids = [$scope.model.selectedNaics];
                else  // groups
                    $scope.peakReportModel.entity_ids = [$scope.model.selectedGroup];
            };

            $scope.submit = function(){
                // remove all models
                $scope.intensityModel = undefined;
                $scope.naicsNodes = [];
                $scope.naicsGroups = [];
                $scope.accountChartRows = [];
                $scope.groupTotalEnergyModel = undefined;
                $scope.naicsTotalEnergyModel = undefined;
                $scope.textReportModel = undefined;
                $scope.peakReportModel = undefined;

                if ($scope.nodes.forceSelectedNodes.length < 1){
                    return false;
                }

                $scope.reportNodes = $scope.nodes.forceSelectedNodes;

                // check to see if the report is on NAICS codes or groups
                if ($scope.reportNodes[0].id.substr(0, 2) === 'g_') { // groups
                    $scope.entityType = 'group';
                } else { // naics
                    $scope.entityType = 'naics';
                }

                // sort the report nodes alphanumerically by specifying the comparison operator for sorting
                // for more information http://www.javascriptkit.com/javatutors/arraysort2.shtml
                $scope.reportNodes = $scope.reportNodes.sort(function(a, b) {
                    var aName = a.name.toLowerCase(), bName = b.name.toLowerCase();
                    if (aName < bName) { return -1; }
                    if (aName > bName) { return 1; }
                    return 0;
                });

                // remove the prefix of all the id's since we know the entityType now
                $scope.reportNodes = $scope.reportNodes.map(function (node) {
                    return {'id': node.id.substring(2), 'childIds': node.childIds, 'name': node.name }
                });

                if ($scope.model.report_type === 'text') {
                    $scope.textReportModel = angular.copy($scope.model);
                    $scope.textReportModel.entity_ids = $scope.reportNodes.map(function (node) {
                        return node.id
                    });

                    // reset naics and groups information
                    $scope.naicsChangeFunction = undefined;
                    $scope.model.selectedNaics = undefined;

                    $scope.groupChangeFunction = undefined;
                    $scope.model.selectedGroup = undefined;
                }
                else if($scope.model.report_type === 'peak') {
                    if ($scope.entityType === 'naics') {
                        // hide all group information
                        $scope.naicsGroups = [];
                        $scope.groupChangeFunction = undefined;

                        $scope.naicsNodes = $scope.reportNodes;
                        $scope.model.selectedNaics = undefined; // the watch function will see this and populate it
                        $scope.naicsChangeFunction = $scope.createPeakReport;
                    } else { // group report
                        // hide all naics information
                        $scope.naicsNodes = [];
                        $scope.naicsChangeFunction = undefined;

                        $scope.naicsGroups = $scope.reportNodes;
                        $scope.model.selectedGroup = undefined; // the watch function will see this and populate it
                        $scope.groupChangeFunction = $scope.createPeakReport;
                    }
                }
                else {
                    if ($scope.model.report_type === "consumption"){
                        $scope.model.entity_ids = $scope.reportNodes.map(function(record) { return record.id });
                        $scope.intensityModel = angular.copy($scope.model);
                    }

                    if ($scope.entityType === 'naics') {
                        // populate list of naics codes
                        $scope.naicsNodes = $scope.reportNodes;
                        // selectedNaics will be set later, when the 'watch' function is ran
                        $scope.model.selectedNaics = undefined;

                        $scope.naicsChangeFunction = $scope.createNaicsConsumptionCharts;
                    } else {
                        // clear out everything with naics to hide it
                        $scope.naicsNodes = [];
                        $scope.model.selectedNaics = undefined;
                        $scope.naicsChangeFunction = undefined;

                        // set the groups list
                        $scope.naicsGroups = $scope.reportNodes;
                    }
                    $scope.model.selectedGroup = undefined;
                    $scope.groupChangeFunction = $scope.createGroupConsumptionCharts;
                }
            };

            $scope.createNaicsConsumptionCharts = function() {
                $scope.naicsTotalEnergyModel = angular.copy($scope.model);
                $scope.naicsTotalEnergyModel.entity_ids = [$scope.model.selectedNaics];
            };

            $scope.createGroupConsumptionCharts = function(){
                var group_id = $scope.model.selectedGroup;

                $scope.consumptionModels = [];
                $scope.accountChartRows = [];

                if ($scope.model.report_type === 'consumption') {
                    $scope.groupTotalEnergyModel = angular.copy($scope.model);
                    $scope.groupTotalEnergyModel.entity_ids = [group_id];
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

            $scope.treeOptions = {
                dataTextField: "name",
                dataSource:{
                    transport:{
                        read: {
                            url:'/api/Naics/getChildrenOf',
                            dataType:"json"
                        }
                    },
                     schema:{
                         model:{
                             id:"id",
                             hasChildren:"childIds.length > 0"
                         }
                     }
                },
                checkboxes:{children:false},
                reporting:true
            };

            var queryParams = $location.search();
            if (queryParams.report_id) {
                // send from the dashboard for a quick report, so get the report and run it.
                $scope.quickReport = true;
                savedReportConfigurationService.getConfigurationById({id: queryParams.report_id}, function (data) {
                    $scope.nodes.selectedNodes = data.config.entity_ids;
                    $scope.model = data.config.configuration;
                    $scope.selectedConfig = queryParams.report_id;
                    $scope.exporting = true;
                    var postUrl = undefined;
                    var reportModel = angular.copy(data.config.configuration);
                    if (data.config.entity_ids.length == 1) {
                        $http.get("/api/Naics/getChildrenOf?id=" + data.config.entity_ids[0].id + "&restrict_type=true")
                            .then(function (d) {
                                reportModel.entity_ids = d.data.length ? d.data : data.config.entity_ids.slice(0);

                                // check to see if the report is on NAICS codes or groups
                                if (reportModel.entity_ids[0].id.substr(0, 2) === 'g_') { // groups
                                    $scope.entityType = 'group';
                                    postUrl = '/api/ReportingGroups/GetReport';
                                } else { // naics
                                    $scope.entityType = 'naics';
                                    postUrl = '/api/ReportingNaics/GetReport';
                                }

                                // sort the report nodes alphanumerically by specifying the comparison operator for sorting
                                // for more information http://www.javascriptkit.com/javatutors/arraysort2.shtml
                                reportModel.entity_ids = reportModel.entity_ids.sort(function(a, b) {
                                    var aName = a.name.toLowerCase(), bName = b.name.toLowerCase();
                                    if (aName < bName) { return -1; }
                                    if (aName > bName) { return 1; }
                                    return 0;
                                });

                                // remove the prefix of all the id's since we know the entityType now
                                reportModel.entity_ids = reportModel.entity_ids.map(function (node) {
                                    return {'id': node.id.substring(2), 'childIds': node.childIds, 'name': node.name }
                                });

                                $scope.exporting = true;
                                reportModel.entity_ids = reportModel.entity_ids.map(function(entry) {return entry.id});
                                reportModel.submitted_to = $rootScope.global.reportingGroup.id;
                                $http.post(postUrl, reportModel, {responseType: 'arraybuffer'})
                                    .success(function(data) {
                                        var file = new Blob([data], {type: 'application/pdf'});
                                        var fileURL = URL.createObjectURL(file);
                                        $scope.pdfurl = fileURL;
                                });
                            });
                    } else {
                        $scope.nodes.forceSelectedNodes = $scope.nodes.selectedNodes.slice(0);

                        // check to see if the report is on NAICS codes or groups
                        if (reportModel.entity_ids[0].id.substr(0, 2) === 'g_') { // groups
                            $scope.entityType = 'group';
                            postUrl = '/api/ReportingGroups/GetReport';
                        } else { // naics
                            $scope.entityType = 'naics';
                            postUrl = '/api/ReportingNaics/GetReport';
                        }

                        // sort the report nodes alphanumerically by specifying the comparison operator for sorting
                        // for more information http://www.javascriptkit.com/javatutors/arraysort2.shtml
                        reportModel.entity_ids = reportModel.entity_ids.sort(function(a, b) {
                            var aName = a.name.toLowerCase(), bName = b.name.toLowerCase();
                            if (aName < bName) { return -1; }
                            if (aName > bName) { return 1; }
                            return 0;
                        });

                        // remove the prefix of all the id's since we know the entityType now
                        reportModel.entity_ids = reportModel.entity_ids.map(function (node) {
                            return {'id': node.id.substring(2), 'childIds': node.childIds, 'name': node.name }
                        });

                        $scope.exporting = true;
                        reportModel.entity_ids = reportModel.entity_ids.map(function(entry) {return entry.id});
                        reportModel.submitted_to = $rootScope.global.reportingGroup.id;
                        $http.post(postUrl, reportModel, {responseType: 'arraybuffer'})
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