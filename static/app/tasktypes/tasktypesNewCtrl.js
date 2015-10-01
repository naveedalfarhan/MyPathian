angular.module("pathianApp.controllers")
    .controller("tasktypesNewCtrl", [
        "$scope", "$rootScope", "$location", "taskTypeService",
        function ($scope, $rootScope, $location, taskTypeService) {
            $rootScope.global.linkpath = "#/admin/tasktypes";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                taskTypeService.save($scope.model, function () {
                    $location.path("/admin/tasktypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/tasktypes');
            }

            $scope.cancel = function () {
                $location.path('/admin/tasktypes');
            };
        }
    ]);
