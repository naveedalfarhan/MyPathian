angular.module("pathianApp.controllers")
    .controller("ecoListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/eco";

            $scope.ecoGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Eco",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name:{type:"string"},
                        p_name:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title:"Project",
                        field:"p_name"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/eco/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/eco/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/eco/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "name", dir:"asc" }
            });
        }
    ]);