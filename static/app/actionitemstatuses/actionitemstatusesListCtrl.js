angular.module("pathianApp.controllers")
    .controller("actionitemstatusesListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/admin/actionitemstatuses";

            $scope.actionitemstatusGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "ActionItemStatuses",
                model: {
                    id: "id",
                    fields: {
                        id: {type:"string", editable: false, nullable: true, defaultValue: undefined, visible:false},
                        name: {type: "string", editable:false}
                    }
                },
                columns: [
                    {
                        title: "Name",
                        template: "#=name#"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/actionitemstatuses/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/actionitemstatuses/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/actionitemstatuses/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "name", dir: "asc" }
            });
        }
    ]);