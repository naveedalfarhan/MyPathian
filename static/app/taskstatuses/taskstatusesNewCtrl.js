angular.module("pathianApp.controllers")
    .controller("taskstatusesNewCtrl", [
        "$scope", "$rootScope", "$location", "taskStatusService",
        function ($scope, $rootScope, $location, taskStatusService) {
            $rootScope.global.linkpath = "#/admin/taskstatuses";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                taskStatusService.save($scope.model, function () {
                    $location.path("/admin/taskstatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

             $scope.cancel = function () {
                $location.path('/admin/taskstatuses');
            }
        }
    ]);
