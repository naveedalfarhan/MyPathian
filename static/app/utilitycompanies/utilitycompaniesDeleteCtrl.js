angular.module("pathianApp.controllers")
    .controller("utilitycompaniesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "utilitycompanyService",
        function ($scope, $rootScope, $location, $routeParams, utilitycompanyService) {
            $rootScope.global.linkpath = "#/admin/utilitycompanies";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            utilitycompanyService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/utilitycompanies")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                utilitycompanyService["delete"](model, function(){
                   $location.path("/admin/utilitycompanies");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);