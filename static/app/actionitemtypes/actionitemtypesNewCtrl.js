angular.module("pathianApp.controllers")
    .controller("actionitemtypesNewCtrl", [
        "$scope", "$rootScope", "$location", "actionitemtypeService",
        function ($scope, $rootScope, $location, actionitemtypeService) {
            $rootScope.global.linkpath = "#/admin/actionitemtypes";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                actionitemtypeService.save($scope.model, function () {
                    $location.path("/admin/actionitemtypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path('/admin/actionitemtypes');
            };
        }
    ]);
