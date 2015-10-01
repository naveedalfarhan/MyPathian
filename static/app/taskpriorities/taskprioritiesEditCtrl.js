angular.module("pathianApp.controllers")
    .controller("taskprioritiesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskPriorityService",
        function ($scope, $rootScope, $location, $routeParams, taskPriorityService) {
            $rootScope.global.linkpath = "#/admin/taskpriorities";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            taskPriorityService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                taskPriorityService.update($scope.model, function(){
                    $location.path("/admin/taskpriorities");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/taskpriorities');
            }
        }
    ]);
