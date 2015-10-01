angular.module("pathianApp.controllers")
    .controller("usersListCtrl", [
        "$scope", "$rootScope", "$location", 
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/admin/users";

            $scope.selected = "nothing";
            $scope.change = function(e) {
                console.log("change");
                console.log(e);
                console.log(this);
            };

            $scope.userGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Users",
                model: {
                    id: "id",
                    fields: {
                        Id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                        username: { type: "string", validation: { required: true } }
                    }
                },
                columns: [
                    "username",
                    {
                        command: [
                            {
                                name: "edit",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/users/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/users/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ],
                        title: "&nbsp;"
                    }
                ],
                editable: false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/users/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort: { field: "username", dir: "asc" }
            });
        }
    ]);