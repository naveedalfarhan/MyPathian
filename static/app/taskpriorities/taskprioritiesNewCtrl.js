angular.module("pathianApp.controllers")
    .controller("taskprioritiesNewCtrl", [
        "$scope", "$rootScope", "$location", "taskPriorityService",
        function ($scope, $rootScope, $location, taskPriorityService) {
            $rootScope.global.linkpath = "#/admin/taskpriorities";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                taskPriorityService.save($scope.model, function () {
                    $location.path("/admin/taskpriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/taskpriorities');
            };
        }
    ]);
