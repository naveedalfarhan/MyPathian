angular.module("pathianApp.controllers")
    .controller("groupsListCtrl", ["$scope", "$rootScope", "$location",
        function ($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/admin/groups";
            
            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "groups",
                model: {
                    id: "id",
                    fields: {
                        Id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                        Name: { type: "string", validation: { required: true } }
                    }
                },
                columns: ["name",
                    {
                        command:
                        [{
                                name: "edit",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/groups/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            }],
                        title: "&nbsp;"
                    }
                ],
                editable: false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/groups/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort: { field: "Name", dir: "asc" },
                other: {
                    filterable: {
                        extra: false,
                        operators: {
                            string: {
                                startswith: "Starts with",
                                eq: "Is equal to"
                            }
                        }
                    }
                }
            });
        }
    ]);