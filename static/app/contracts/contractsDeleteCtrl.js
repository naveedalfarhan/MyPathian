angular.module("pathianApp.controllers")
    .controller("contractsDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "contractService",
        function ($scope, $rootScope, $location, $routeParams, contractService) {
            $rootScope.global.linkpath = "#/admin/contracts";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            contractService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/contracts")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                contractService["delete"](model, function(){
                   $location.path("/admin/contracts");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);