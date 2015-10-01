angular.module("pathianApp.controllers")
    .controller("groupsAccountManagerCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "groupTreeFactory", "$compile",
        function ($scope, $rootScope, $location, $http, $modal, groupTreeFactory, $compile) {
            $rootScope.global.linkpath = "#/admin/groups/accounts";

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
                        toolbar: [
                            {template: "<a class='k-button k-button-icontext k-grid-add' ng-click='addAccount($event)'><span class='k-icon k-add'></span>Add account</a>"}
                        ],
                        columns: ["name", "num", "type",
                            {
                                command: [
                                    {
                                        template: "<a class='k-button k-button-icontext k-grid-edit' ng-click='editAccount($event)'><span class='k-icon k-edit'></span>Edit</a>"
                                    },
                                    {
                                        template: "<a class='k-button k-button-icontext k-grid-delete' ng-click='deleteAccount($event)'><span class='k-icon k-delete'></span>Delete</a>"
                                    }
                                ]
                            }
                        ],
                        editable: false
                    }
				};
			};

            var setPriceAndSizeGridOptions = function(acct_id) {
                $scope.priceGridOptions = $rootScope.global.getJsonGridOptions({
                    controllerName: "accounts/" + acct_id + "/pricenormalizations",
                    model: {
                        id: "id",
                        fields: {
                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                            effective_date: { type: "date", validation: { required: true } },
                            value: { type: "number", validation: { required: true } },
                            note: { type: "string", validation: {required: false } }
                        }
                    },
                    columns: [
                        {field: "effective_date", title: "Effective Date", template: "#= kendo.toString(effective_date, 'MM/dd/yyyy') #"},
                        {field: "value", title: "Value"},
                        {field: "note", title: "Note"},
                        {
                            command: ["edit", "destroy"], title: "&nbsp;", width: "172px"
                        }
                    ],
                    editable: "inline",
                    toolbar: ["create"],
                    defaultSort: { field: "effective_date", dir: "asc" }
                });

                $scope.sizeGridOptions = $rootScope.global.getJsonGridOptions({
                    controllerName: "accounts/" + acct_id + "/sizenormalizations",
                    model: {
                        id: "id",
                        fields: {
                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                            effective_date: { type: "date", validation: { required: true } },
                            value: { type: "number", validation: { required: true } },
                            note: { type: "string", validation: {required: false } }
                        }
                    },
                    columns: [
                        {field: "effective_date", title: "Effective Date", template: "#= kendo.toString(effective_date, 'MM/dd/yyyy') #"},
                        {field: "value", title: "Value"},
                        {field: "note", title: "Note"},
                        {
                            command: ["edit", "destroy"], title: "&nbsp;", width: "172px"
                        }
                    ],
                    editable: "inline",
                    toolbar: ["create"],
                    defaultSort: { field: "effective_date", dir: "asc" }
                });
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
                $("#priceGrid").empty();
                $("#sizeGrid").empty();

                if (!$scope.model.selectedAccount)
                    return;

                var $priceGrid = $("<div id='priceGrid' kendo-grid k-options='priceGridOptions.options' k-data-source='priceGridOptions.dataSource'></div>");
                $("#priceGrid").append($priceGrid);

                var $sizeGrid = $("<div id='sizeGrid' kendo-grid k-options='sizeGridOptions.options' k-data-source='sizeGridOptions.dataSource'></div>");
                $("#sizeGrid").append($sizeGrid);

                setPriceAndSizeGridOptions($scope.model.selectedAccount.id);

                $compile($priceGrid)($scope);
                $compile($sizeGrid)($scope);
            });

            $scope.addAccount = function(event) {
                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                $scope.launchAccountEditor(null, grid);
            };

            $scope.editAccount = function(event) {
                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                $scope.launchAccountEditor(this.dataItem, grid);
            };

            $scope.deleteAccount = function(event) {
                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                var account = this.dataItem;

                var modalWindow = $modal.open({
                    templateUrl: "accountDelete.html",
                    controller: ["$scope", "accountService",
                        function($innerScope, accountService) {
                            $innerScope.model = accountService.get({id: account.id});

                            $innerScope.cancel = function() {
                                modalWindow.close();
                                return false;
                            };

                            $innerScope.submit = function() {
                                accountService.delete({id: $innerScope.model.id}, function () {
                                    modalWindow.close();
                                    grid.dataSource.read();
                                });
                            };
                        }
                    ]
                });

                return false;
            };

            $scope.launchAccountEditor = function(account, grid) {
                var mode = account ? "edit" : "create";
                var modalWindow = $modal.open({
                    size: "lg",
                    templateUrl: "accountEditor.html",
                    controller: ["$scope", "weatherstationService", "timezoneService", "accountService",
                        function($innerScope, weatherstationService, timezoneService, accountService) {
                            $innerScope.mode = mode;
                            $innerScope.caption = mode == "edit" ? "Edit Account" : "Add Account";

                            $innerScope.weatherstations = weatherstationService.list();
                            $innerScope.timezones = timezoneService.query();
                            $innerScope.accountTypes = [
                                {id: "electric", name: "Electric"},
                                {id: "gas", name: "Gas"}
                            ];

                            if (account) {
                                $innerScope.model = accountService.get({id: account.id});
                            } else {
                                $innerScope.model = {};
                            }

                            $innerScope.model.group_id = $scope.model.selectedGroup ? $scope.model.selectedGroup.id : null;

                            $innerScope.cancel = function() {
                                modalWindow.close();
                                return false;
                            };

                            $innerScope.submit = function() {
                                var model = $innerScope.model;
                                if (!model.name || !model["type"] || !model.weatherstation_id || !model.timezone) {
                                    return;
                                }
                                if (mode == "create" && (!model.initial_price_normalization || !model.initial_size_normalization)) {
                                    return;
                                }

                                if (model.id) {
                                    accountService.update($innerScope.model, function () {
                                        modalWindow.close();
                                        grid.dataSource.read();
                                    });
                                } else {
                                    accountService.save($innerScope.model, function () {
                                        modalWindow.close();
                                        grid.dataSource.read();
                                    });
                                }
                            };
                        }
                    ]
                })
            };
        }
    ]);