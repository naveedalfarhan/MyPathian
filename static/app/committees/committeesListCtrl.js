angular.module("pathianApp.controllers")
    .controller("committeesListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/committees";

            $scope.committeeGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Committees",
                model: {
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name:{type:"string"},
                        g_name:{type:"string"},
                        c_e_d:{type:"string"}
                    }
                },
                columns:[
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title:"Group",
                        field:"g_name"
                    },
                    {
                        title:"Corporate Energy Director",
                        field:"c_e_d"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/committees/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/committees/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/committees/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{field:"name", dir:"asc"}
            });
        }
    ]);