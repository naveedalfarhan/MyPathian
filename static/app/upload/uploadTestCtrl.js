angular.module("pathianApp.controllers")
    .controller("uploadTestCtrl", [
        "$scope", "$rootScope", "$location",
        function ($scope, $rootScope, $location) {
            $scope.options = {
                url: "/api/upload"
            };
        }
    ]);