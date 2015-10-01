angular.module("pathianApp.controllers")
    .controller("contactsEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "contactService", "groupService", "categoryService",
        function ($scope, $rootScope, $location, $routeParams, contactService, groupService, categoryService) {
            $rootScope.global.linkpath = "#/commissioning/contacts";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            contactService.get({id:$scope.id}, function(model) {
                if (model.group_id === null)
                    model.group = null;
                else
                    model.group = {
                        id: model.group_id,
                        name: "?"
                    };

                if (model.category_id === null)
                    model.category = null;
                else
                    model.category = {
                        id: model.category_id,
                        name: "?"
                    };

                categoryService.get({id:model.category_id}, function(categoryModel){
                    model.category.name = categoryModel.name;
                });

                groupService.get({id:model.group_id}, function(groupModel) {
                    model.group.name = groupModel.name;
                });
                $scope.model = model;
            });

            $scope.categories = new Array;

            categoryService.GetAll({}, function(list){
                $scope.categories = list;
            });

            $scope.submit = function(){
                if ($scope.model.group === null)
                    $scope.model.group_id = "";
                else
                    $scope.model.group_id = $scope.model.group.id

                contactService.update($scope.model, function(){
                    $location.path("/commissioning/contacts");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "groups",
                model:{
                    id: "id",
                    fields: {
                        Id: { type:"string", editable:false, nullable:true, defaultValue:undefined },
                        name: { type:"string", validation: {required:true}}
                    }
                },
                columns:["name"],
                editable:false,
                createTemplate:false,
                defaultSort: {field:"name", dir:"asc"}
            });

            $scope.cancel = function () {
                $location.path("/commissioning/contacts");
            }
        }
    ]);
