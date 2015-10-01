angular.module("pathianApp.controllers")
    .controller("issuetypesNewCtrl", [
        "$scope", "$rootScope", "$location", "issueTypeService",
        function ($scope, $rootScope, $location, issueTypeService) {
            $rootScope.global.linkpath = "#/admin/issuetypes";

            $scope.showErrorMessage = false;

            $scope.submit = function () {
                issueTypeService.save($scope.model, function () {
                    $location.path("/admin/issuetypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

             $scope.cancel = function(){
                $location.path("/admin/issuetypes");
            };
        }
    ]);
