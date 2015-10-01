/**
 * Created by badams on 1/14/2015.
 */
angular.module('pathianApp.controllers')
    .controller('viewDataCtrl', ['$rootScope', '$scope', '$compile', 'accountService',
        function($rootScope, $scope, $compile, accountService) {
            $rootScope.global.linkpath = "#/reporting/accounts/viewData";

            $scope.model = {
                selectedGroup: null,
                selectedAccount: null
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
                }
            };

            $scope.dataGridOptions = undefined;


			var setAccountGridOptions = function(groupId) {
				$scope.accountGridOptions = {
					dataSource: {
						transport: {
							read: {
								url: "/api/accounts/for_group/" + groupId,
								dataType: "json",
								contentType: "application/json",
								type: "GET"
							}
						},
						schema: {
                            data: "data",
							total: "total",
							model: {
								id: "id",
								fields: {
									id: { type: "string"},
									name: { type: "string"},
									num: { type: "string"},
									type: { type: "string"}
								}
							}
						},
						pageSize: 10,
						serverPaging: true
					},
                    options: {
                        scrollable: false,
                        filterable: false,
                        sortable: false,
                        pageable: true,
                        columns: ["name", "num", "type"],
                        editable: false
                    }
				};
			};

            $scope.$watch("model.selectedGroup", function() {
                // reset everything
                $("#accountGrid").empty();
                $("#priceGrid").empty();
                $("#sizeGrid").empty();
                $scope.model.selectedAccount = null;

				if (!$scope.model.selectedGroup)
					return;

				var $grid = $("<div id='accountGrid' single-picker='model.selectedAccount' single-picker-options='accountGridOptions' ng-required='true' single-picker-key-prop='id' single-picker-caption-prop='name'></div>");
				$("#accountGrid").append($grid);
				setAccountGridOptions($scope.model.selectedGroup.id);
				$compile($grid)($scope);
			});

            $scope.$watch("model.selectedAccount", function() {
                // reset the date pickers and add submit button
                $(".account-data-datepicker").val("");
                $scope.dateOptions.start_date = undefined;
                $scope.dateOptions.end_date= undefined;

                $scope.dataGridOptions = undefined;
            });

            $scope.findData = function(){
                accountService.get({id:$scope.model.selectedAccount.id}, function(data) {
                    var type = data.type;

                    // transform the start and end date to epoch time to send in the query string
                    var startDateEpoch = Math.floor((new Date($scope.dateOptions.start_date)).getTime()/1000);
                    var endDateEpoch = Math.floor((new Date($scope.dateOptions.end_date)).getTime()/1000);

                    var fields = {};
                    var columnHeaders = [];
                    if (type == 'electric') {
                        fields = {
                            id: { type: "string", visible: false },
                            'readingdatelocal': {type: "string" },
                            'readingdateutc': { type: "string" },
                            'energy.kwh': { type: "decimal" },
                            'energy.kvar': { type: "decimal" },
                            'energy.kva': { type: "decimal" },
                            'energy.pf': { type: "decimal" }
                        };

                        columnHeaders = [
                            {title: "Reading Date Local", field: "readingdatelocal"},
                            {title: "Reading Date UTC", field:"readingdateutc"},
                            {title: "kWh", field:"energy.kwh", template: "#= kendo.format('{0:0.00}', energy.kwh) #" },
                            {title: "kVar", field:"energy.kvar", template: "#= kendo.format('{0:0.00}', energy.kvar) #" },
                            {title: "kVa", field:"energy.kva", template: "#= kendo.format('{0:0.00}', energy.kva) #" },
                            {title: "Pf", field:"energy.pf", template: "#= kendo.format('{0:0.00000}', energy.pf) #" }
                        ]

                    } else {
                        fields = {
                            id: { type: "string", visible: false },
                            'readingdatelocal': { type: "string" },
                            'readingdateutc': { type: "string" },
                            'energy.mcf': { format: "{0:c3}" }
                        };

                        columnHeaders = [
                            { title: "Reading Date Local", field: "readingdatelocal" },
                            { title: "Reading Date UTC", field: "readingdateutc"},
                            { title: "Mcf", field:"energy.mcf", template: "#= kendo.format('{0:0.00}', energy.mcf) #" }
                        ];
                    }

                    $scope.dataGridOptions = {
                        dataSource: {
                            transport: {
                                read: {
                                    url: "/api/reporting/accounts/" + $scope.model.selectedAccount.id + "?start_date=" + startDateEpoch + "&end_date=" + endDateEpoch,
                                    dataType: "json",
                                    contentType: "application/json",
                                    type: "GET"
                                }
                            },
                            schema: {
                                data: "data",
                                total: "total",
                                model: {
                                    id: "id",
                                    fields: fields
                                }
                            },
                            pageSize: 10,
                            serverPaging: true,
                            serverSorting: true,
                            serverFiltering: true,
                            sort: { field: "readingdateutc", dir: "asc" }
                        },
                        options: {
                            sortable: { mode: "single" },
                            scrollable: false,
                            filterable: true,
                            pageable: true,
                            columns: columnHeaders,
                            editable: false,
                            resizeable: true
                        }
                    };
                });
            };

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format = 'MM/dd/yyyy';
        }
    ]);