angular.module("pathianApp.controllers")
    .controller("tasktypesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskTypeService",
        function ($scope, $rootScope, $location, $routeParams, taskTypeService) {
            $rootScope.global.linkpath = "#/admin/tasktypes";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            taskTypeService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/tasktypes")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                taskTypeService["delete"](model, function(){
                   $location.path("/admin/tasktypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);