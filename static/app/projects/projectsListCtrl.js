angular.module("pathianApp.controllers")
    .controller("projectsListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/projects";

            $scope.projectGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Projects",
                model: {
                    id:"id",
                    fields: {
                        id: {type:"string"},
                        name:{type:"string"},
                        customer_project_id:{type:"string"},
                        architect_project_id:{type:"string"},
                        start_date:{type:"string"},
                        complete_date:{type:"string"},
                        estimated_cost:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title:"Customer Project Id",
                        field:"customer_project_id"
                    },
                    {
                        title:"Architect Project Id",
                        field:"architect_project_id"
                    },
                    {
                        title:"Start Date",
                        field:"start_date"
                    },
                    {
                        title:"Completed Date",
                        field: "complete_date"
                    },
                    {
                        title:"Estimated Cost",
                        template:"$#= estimated_cost #"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/projects/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/projects/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/projects/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "first_name", dir: "asc" }
            });
        }
    ]);