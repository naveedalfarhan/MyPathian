angular.module("pathianApp.controllers")
    .controller("issuestatusesNewCtrl", [
        "$scope", "$rootScope", "$location", "issueStatusService",
        function ($scope, $rootScope, $location, issueStatusService) {
            $rootScope.global.linkpath = "#/admin/issuestatuses";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                issueStatusService.save($scope.model, function () {
                    $location.path("/admin/issuestatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/issuestatuses");
            };
        }
    ]);
