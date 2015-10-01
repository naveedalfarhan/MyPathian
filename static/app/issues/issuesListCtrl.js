angular.module("pathianApp.controllers")
    .controller("issuesListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/issues";

            $scope.issueGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Issues",
                model: {
                    id:"id",
                    fields:{
                        id:{type:"string", editable:false, nullable:true, defaultValue:undefined, visible:false},
                        name:{type:"string", editable:false}
                    }
                },
                columns:[
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title:"Open Date",
                        field:"open_date"
                    },
                    {
                        title:"Due Date",
                        field:"due_date"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/issues/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/issues/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/issues/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{field:"name", dir:"asc"}
            });
        }
    ]);