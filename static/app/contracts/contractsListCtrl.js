angular.module("pathianApp.controllers")
    .controller("contractsListCtrl", [
        "$scope", "$rootScope", "$location", "$compile",
        function($scope, $rootScope, $location, $compile) {
            $rootScope.global.linkpath = "#/admin/contracts";

            $scope.contractGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Contracts",
                model: {
                    id: "id",
                    fields: {
                        id: {type:"string", editable: false, nullable: true, defaultValue: undefined, visible:false},
                        name: {type: "string", editable:false},
                        start_date: {type: "date", editable:false},
                        end_date: {type: "date", editable:false},
                        active: {type: "bool", editable:false},
                        group_name: {type: "string", editable:false},
                        purchase_order_number: {type: "string", editable:false},
                        dollar_amount: {type: "string", editable:false}
                    }
                },
                columns: [
                    {
                        title: "Name",
                        template: "#=name#"
                    },
                    {
                        title: "Active",
                        template: "#=active#"
                    },
                    {
                        title: "Purchase Order #",
                        template: "#=purchase_order_number#"
                    },
                    {
                        title: "Dollar Amt",
                        template: "#=dollar_amount#"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/contracts/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/contracts/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/contracts/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "name", dir: "asc" }
            });


            var setUserGridOptions = function(contract_id) {
				$scope.userGridOptions = {
					dataSource: {
						transport: {
							read: {
								url: "/api/Contracts/Users/" + contract_id,
								dataType: "json",
								contentType: "application/json",
								type: "GET"
							}
						},
						schema: {
							model: {
								id: "id",
								fields: {
									id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
									username: { type: "string", validation: { required: false } }
								}
							}
						},
						pageSize: 10,
						serverPaging: true
					},
					pageable: true,
					columns: [
						{
							field:"username",
							title:"Username"
						}
					]
				};
			};

            $scope.$watch("selectedNode", function() {
				if (!$scope.selectedNode)
					return;

				var $grid = $("<div id='userGridContainer'><p>Users</p><div id='userGrid' kendo-grid k-options='userGridOptions' k-data-source='userGridOptions.dataSource'></div></div>");
				$("#userGridContainer").replaceWith($grid);
				setUserGridOptions($scope.selectedNode.id);
				$compile($grid)($scope);
			});
        }
    ]);