angular.module("pathianApp.controllers")
    .controller("actionitemstatusesNewCtrl", [
        "$scope", "$rootScope", "$location", "actionitemstatusService",
        function ($scope, $rootScope, $location, actionitemstatusService) {
            $rootScope.global.linkpath = "#/admin/actionitemstatuses";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                actionitemstatusService.save($scope.model, function () {
                    $location.path("/admin/actionitemstatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/actionitemstatuses');
            }
        }
    ]);
