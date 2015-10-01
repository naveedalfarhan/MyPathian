angular.module('pathianApp.controllers')
    .controller("syrxCategoriesListCtrl", [
        "$scope", "$rootScope", "$location",
        function($scope, $rootScope, $location){
            $rootScope.global.linkpath = '#/admin/syrxcategories';

            $scope.syrxCategoryGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "SyrxCategories",
                model: {
                    id:"id",
                    fields:{
                        id: {type:"string", editable:false, nullable:true, defaultValue:undefined, visible:false},
                        name: {type:"string", editable:false}
                    }
                },
                columns:[
                    {
                        title:"Name",
                        field:"name"
                    },
                    {
                        title: "",
                        field:"",
                        template: "<a class='k-button k-button-icontext k-grid-edit' href='\\#/admin/syrxcategories/#=id#/edit'><span class='k-icon k-edit'></span>Edit</a>" +
                            "<a class='k-button k-button-icontext k-grid-delete' href='\\#/admin/syrxcategories/#=id#/delete'><span class='k-icon k-delete'></span>Delete</a>"
                    }
                ],
                editable:false,
                createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/admin/syrxcategories/new'><span class='k-icon k-add'></span>Add new record</a>",
                defaultSort: {field:"name", dir:"asc"}
            });
        }
    ]);