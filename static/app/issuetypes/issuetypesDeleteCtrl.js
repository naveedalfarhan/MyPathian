angular.module("pathianApp.controllers")
    .controller("issuetypesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueTypeService",
        function ($scope, $rootScope, $location, $routeParams, issueTypeService) {
            $rootScope.global.linkpath = "#/admin/issuetypes";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            issueTypeService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/issuetypes")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                issueTypeService["delete"](model, function(){
                   $location.path("/admin/issuetypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);