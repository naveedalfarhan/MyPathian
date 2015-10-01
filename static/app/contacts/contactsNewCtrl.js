angular.module("pathianApp.controllers")
    .controller("contactsNewCtrl", [
        "$scope", "$rootScope", "$location", "contactService", "groupService", "categoryService",
        function ($scope, $rootScope, $location, contactService, groupService, categoryService) {
            $rootScope.global.linkpath = "#/commissioning/contacts";

            $scope.showErrorMessage = false;

            $scope.model = {
                group: null
            };
            $scope.submit = function () {
                if ($scope.model.group === null)
                    $scope.model.group_id = "";
                else
                    $scope.model.group_id = $scope.model.group.id
                contactService.save($scope.model, function () {
                    $location.path("/commissioning/contacts");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.categories = new Array;

            categoryService.GetAll({}, function(list){
                $scope.categories = list;
            });

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "groups",
                model:{
                    id: "id",
                    fields:{
                        id: { type:"string", editable:false, nullable:true, defaultValue:undefined },
                        name: { type:"string", validation: {required:true}}
                    }
                },
                columns:[{
                    field:"name",
                    title:"Name"
                }],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"name",dir:"asc"}
            });

            $scope.cancel = function () {
                $location.path("/commissioning/contacts");
            }
        }
    ]);
