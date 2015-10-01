angular.module("pathianApp.controllers")
    .controller("taskprioritiesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskPriorityService",
        function ($scope, $rootScope, $location, $routeParams, taskPriorityService) {
            $rootScope.global.linkpath = "#/admin/taskpriorities";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            taskPriorityService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/taskpriorities")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                taskPriorityService["delete"](model, function(){
                   $location.path("/admin/taskpriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);