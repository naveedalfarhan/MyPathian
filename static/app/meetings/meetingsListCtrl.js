angular.module("pathianApp.controllers")
    .controller("meetingsListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/meetings";

            $scope.meetingsGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName:"Meetings",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        title:{type:"string"},
                        date:{type:"string"},
                        location:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Title",
                        field:"title"
                    },
                    {
                        title:"Date",
                        field:"date"
                    },
                    {
                        title:"Location",
                        field:"location"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/meetings/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/meetings/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/meetings/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "title", dir: "asc" }
            });
        }
    ]);