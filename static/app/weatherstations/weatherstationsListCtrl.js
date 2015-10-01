angular.module("pathianApp.controllers")
    .controller("weatherstationsListCtrl", ["$scope", "$rootScope", "$location",
        function ($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/admin/weatherstations";
            
            $scope.weatherstationGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "weatherstations",
                model: {
                    id: "id",
                    fields: {
                        id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                        name: { type: "string", validation: { required: true } },
                        usaf: { type: "string", validation: { required: true } },
                        wban: { type: "string", validation: { required: true } },
                        years: { type: "string", validation: { required: true } }
                    }
                },
                columns: [
                    {field: "name", title: "Name"},
                    {field: "usaf", title: "USAF"},
                    {field: "wban", title: "WBAN"},
                    {field: "years", title: "Populated Years", sortable: false, filterable: false},
                    {
                        command:
                        [{
                                name: "edit",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/weatherstations/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/admin/weatherstations/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }],
                        title: "&nbsp;"
                    }
                ],
                editable: false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/weatherstations/new'><span class='k-icon k-add'></span>Add new weatherstation</a>",
                defaultSort: { field: "Name", dir: "asc" }
            });
        }
    ]);