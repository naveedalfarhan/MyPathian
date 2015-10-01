angular.module("pathianApp.controllers")
    .controller("equipmentListCtrl", ["$scope", "$rootScope", "$location",
        function ($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/equipment";

            var route = $rootScope.global.commissioningGroup ? "equipmentForGroup/" + $rootScope.global.commissioningGroup.id : "equipment";

            $scope.model = {selectedGroup: null};

            $scope.$watch("model.selectedGroup", function() {
                $scope.selectedGroup = $scope.model.selectedGroup;
            });

            $scope.groupTreeOptions = {
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

            $scope.equipmentGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: route,
                model: {
                    id: "id",
                    fields: {
                        id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                        num: { type: "string" },
                        name: { type: "string", validation: { required: true } }
                    }
                },
                columns: ["num", "name",
                    {
                        command:
                        [{
                                name: "edit",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/equipment/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/equipment/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "dashboard",
                                template: "<a class='k-button k-button-icontext k-grid-dashboard' href='\\#'><span class='k-icon k-justifyLeft'></span>Dashboard</a>",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/equipment/" + id + "/dashboard");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ],
                        title: "&nbsp;"
                    }
                ],
                editable: false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/equipment/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort: { field: "Name", dir: "asc" }
            });
        }
    ]);