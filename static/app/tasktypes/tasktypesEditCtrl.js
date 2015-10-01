angular.module("pathianApp.controllers")
    .controller("tasktypesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskTypeService",
        function ($scope, $rootScope, $location, $routeParams, taskTypeService) {
            $rootScope.global.linkpath = "#/admin/tasktypes";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            taskTypeService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                taskTypeService.update($scope.model, function(){
                    $location.path("/admin/tasktypes");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/tasktypes');
            }
        }
    ]);
