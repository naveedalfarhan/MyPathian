angular.module("pathianApp.controllers")
    .controller("actionitemprioritiesNewCtrl", [
        "$scope", "$rootScope", "$location", "actionitempriorityService",
        function ($scope, $rootScope, $location, actionitempriorityService) {
            $rootScope.global.linkpath = "#/admin/actionitempriorities";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                actionitempriorityService.save($scope.model, function () {
                    $location.path("/admin/actionitempriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/actionitempriorities");
            };
        }
    ]);
