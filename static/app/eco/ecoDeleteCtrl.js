angular.module("pathianApp.controllers")
    .controller("ecoDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "ecoService",
        function($scope, $rootScope, $location, $routeParams, ecoService) {
            $rootScope.global.linkpath = "#/commissioning/eco";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            ecoService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/eco");
            };

            $scope.submit = function() {
                var model={
                    id:$scope.id
                };
                ecoService["delete"](model, function() {
                    $location.path("/commissioning/eco");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);