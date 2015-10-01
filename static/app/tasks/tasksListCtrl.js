angular.module("pathianApp.controllers")
    .controller("tasksListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/tasks";

            $scope.tasksGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Tasks",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string", visible:false},
                        name:{type:"string"},
                        priority:{type:"string"},
                        status:{type:"string"},
                        task_type:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title:"Priority",
                        field:"priority"
                    },
                    {
                        title:"Status",
                        field:"status"
                    },
                    {
                        title:"Type",
                        field:"task_type"
                    },
                    {
                        command:
                        [{
                                name: "edit",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/tasks/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/tasks/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }],
                        title: "&nbsp;"
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/tasks/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{field:"name",dir:"asc"}
            });
        }
    ]);