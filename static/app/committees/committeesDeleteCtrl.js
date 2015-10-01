angular.module("pathianApp.controllers")
    .controller("committeesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "committeeService",
        function($scope, $rootScope, $location, $routeParams, committeeService) {
            $rootScope.global.linkpath = "#/commissioning/committees";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            committeeService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/committees");
            };

            $scope.submit = function() {
                var model={
                    id:$scope.id
                };
                committeeService["delete"](model, function() {
                    $location.path("/commissioning/committees");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);