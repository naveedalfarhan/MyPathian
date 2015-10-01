angular.module("pathianApp.controllers")
    .controller("contactsListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/commissioning/contacts";

            $scope.contactGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Contacts",
                model: {
                    id: "id",
                    fields: {
                        id: {type:"string", editable: false, nullable: true, defaultValue: undefined, visible:false},
                        first_name: {type: "string", editable:false},
                        last_name: {type:"string", editable:false},
                        title: {type: "string", editable:false},
                        email: {type: "string", editable:false},
                        address: {type: "string", editable:false},
                        city: {type:"string", editable:false},
                        state: {type:"string",editable:false},
                        zip: {type:"string", editable:false}
                    }
                },
                columns: [
                    {
                        title: "Name",
                        template: "#=first_name# #=last_name#"
                    },
                    {
                        title:"Title",
                        template: "#=title#"
                    },
                    {
                        title:"Email",
                        template:"#=email#"
                    },
                    {
                        title:"Address",
                        template:"#=address#<br />#=city#, #=state# #=zip#"
                    },
                    {
                        command: [
                            {
                                name: "edit",
                                click: function (e) {
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/contacts/" + id + "/edit");
                                    $scope.$apply();
                                    return false;
                                }
                            },
                            {
                                name: "delete",
                                template: "<a class='k-button k-button-icontext k-grid-delete' href='\\#'><span class='k-icon k-delete'></span>Delete</a>",
                                click: function(e){
                                    var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                                    $location.path("/commissioning/contacts/" + id + "/delete");
                                    $scope.$apply();
                                    return false;
                                }
                            }
                        ]
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/contacts/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort:{ field: "first_name", dir: "asc" }
            });
        }
    ]);