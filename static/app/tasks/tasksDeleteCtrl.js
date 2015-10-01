angular.module("pathianApp.controllers")
    .controller("tasksDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskService",
        function($scope, $rootScope, $location, $routeParams, taskService) {
            $rootScope.global.linkpath = "#/commissioning/tasks";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            taskService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/commissioning/tasks");
            };

            $scope.submit = function() {
                var model = {
                    id:$scope.id
                };
                taskService["delete"](model, function() {
                    $location.path("/commissioning/tasks");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);