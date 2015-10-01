angular.module("pathianApp.controllers")
    .controller("homeCtrl", ["$scope", "$rootScope", "$location", "savedReportConfigurationService",
        function($scope, $rootScope, $location, savedReportConfigurationService) {
            $rootScope.global.linkpath = "#/home";

            $scope.benchmark_year_list = [];
            for (var i=0; i < 5; ++i) {
                $scope.benchmark_year_list.push(new Date().getFullYear() - i);
            }

            $scope.account_type = 'all';

            if ($rootScope.global.user !== null) {
                $scope.user_id = $rootScope.global.user.id;
            }
            else{
                $scope.user_id = null;
            }

            $scope.savedReports = [];
            $scope.selectedReport = '';

            if (($rootScope.global.user !== null)&& ($rootScope.global.user.primary_group != null)){
                $scope.child_groups = $rootScope.global.user.groups.map(function(entry) { return {'id': entry.id, 'name': entry.name }});
                $scope.selected_group = $rootScope.global.user.primary_group.id;

                $scope.model = {
                    selected_group: $rootScope.global.user.primary_group.id,
                    benchmark_year: new Date().getFullYear() - 1,
                    account_type: 'all',
                    demand_type: 'all',
                    comparison_type: 'temp',
                    start_month: 1,
                    end_month: 12,
                    report_year: new Date().getFullYear(),
                    electric_units: 'kwh',
                    gas_units: 'mcf',
                    btu_units: 'mmbtus',
                    group_ids: [$scope.selected_group],
                    report_type:'consumption'
                };


                $scope.$watch('model.selected_group', function() {
                    $scope.model.group_ids = [$scope.model.selected_group];
                });

                $scope.tasksGridOptions = {
                    dataSource: {
                        transport: {
                            read: "/api/group/" + $rootScope.global.user.primary_group.id + "/Tasks",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        schema: {
                            data: function (response) {
                                return response.data;
                            },
                            total: function (response) {
                                return response.total;
                            },
                            model: {
                                id: "id",
                                fields: {
                                    id: {type: "string", visible: false},
                                    name: {type: "string"},
                                    group: {type: "string"},
                                    equipment: {type: "string"},
                                    description: {type: "string"},
                                    full_name: {type: "string"}
                                }
                            }
                        },
                        pageSize: 10,
                        serverPaging: true,
                        serverFiltering: true,
                        serverSorting: true,
                        sort: 'asc'
                    },
                    options: {
                        columns: [
                            {
                                title: "Group",
                                field: "group"
                            },
                            {
                                title: "Equipment",
                                field: "equipment"
                            },
                            {
                                title: "Task<br>Name",
                                field: "name"
                            },
                            {
                                title: "Task<br>Description",
                                field: "description"
                            },
                            {
                                title: "Assigned<br>To",
                                field: "full_name"
                            }
                        ],
                        editable: false,
                        defaultSort: {field: "name", dir: "asc"},
                        scrollable: false,
                        filterable: true,
                        sortable: { mode: "multiple" },
                        pageable: true,
                        toolbar: false
                    }
                };

                $scope.issuesGridOptions = {
                    dataSource: {
                        transport: {
                            read: "/api/group/" + $rootScope.global.user.primary_group.id + "/issues",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        schema: {
                            data: function(response) {
                                return response.data;
                            },
                            total: function(response) {
                                return response.total;
                            },
                            model: {
                                id: "id",
                                fields: {
                                    id: {type:"string", visible:false},
                                    name: {type:"string"},
                                    group: {type:"string"},
                                    equipment: {type:"string"},
                                    description: {type:"string"}
                                }
                            }
                        },
                        pageSize: 10,
                        serverPaging: true,
                        serverFiltering: true,
                        serverSorting: true,
                        sort: 'asc'
                    },
                    options: {
                        columns: [
                            {
                                title: "Group",
                                field:"group"
                            },
                            {
                                title: "Equipment",
                                field:"equipment"
                            },
                            {
                                title: "Issue Name",
                                field: "name"
                            },
                            {
                                title: "Issue<br>Description",
                                field: "description"
                            }
                        ],
                        editable: false,
                        defaultSort: {field:"name", dir: "asc"},
                        scrollable: false,
                        filterable: true,
                        sortable: { mode: "multiple" },
                        pageable: true,
                        toolbar: false
                    }
                };


                // get saved reports for dropdown
                savedReportConfigurationService.getSavedConfigurationsByType({type:'group'}, function(data) {
                    var configs = data.configs;
                    for(var i=0; i < configs.length; ++i) {
                        configs[i].name = "Group Report - " + configs[i].name;
                        $scope.savedReports.push(configs[i])
                    }

                });
                savedReportConfigurationService.getSavedConfigurationsByType({type:'naics'}, function(data) {
                    var configs = data.configs;
                    for(var i=0; i < configs.length; ++i) {
                        configs[i].name = "NAICS Report - " + configs[i].name;
                        $scope.savedReports.push(configs[i])
                    }
                });
                savedReportConfigurationService.getSavedConfigurationsByType({type:'sic'}, function(data) {
                    var configs = data.configs;
                    for(var i=0; i < configs.length; ++i) {
                        configs[i].name = "SIC Report - " + configs[i].name;
                        $scope.savedReports.push(configs[i])
                    }
                });
            }

            $scope.runReport = function(report_id) {
                if (report_id) {
                    // find configuration
                    var config = undefined;
                    for (var i=0; i < $scope.savedReports.length; i++) {
                        if ($scope.savedReports[i].id === report_id) {
                            config = $scope.savedReports[i];
                            if (config.report_type === 'naics') {
                                $location.path("/reporting/naics").search({report_id:config.id});
                            } else if (config.report_type === 'sic') {
                                $location.path("/reporting/sic").search({report_id:config.id});
                            } else {
                                $location.path("/reporting/groups").search({report_id:config.id});
                            }
                        }
                    }
                }
            }
        }
    ]);