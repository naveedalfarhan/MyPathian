angular.module("pathianApp.controllers")
    .controller("meetingtypesNewCtrl", [
        "$scope", "$rootScope", "$location", "meetingtypeService",
        function ($scope, $rootScope, $location, meetingtypeService) {
            $rootScope.global.linkpath = "#/admin/meetingtypes";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                meetingtypeService.save($scope.model, function () {
                    $location.path("/admin/meetingtypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/meetingtypes");
            }
        }
    ]);
