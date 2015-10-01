angular.module("pathianApp.controllers")
    .controller("issueprioritiesNewCtrl", [
        "$scope", "$rootScope", "$location", "issuePriorityService",
        function ($scope, $rootScope, $location, issuePriorityService) {
            $rootScope.global.linkpath = "#/admin/issuepriorities";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                issuePriorityService.save($scope.model, function () {
                    $location.path("/admin/issuepriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/issuepriorities");
            };
        }
    ]);
