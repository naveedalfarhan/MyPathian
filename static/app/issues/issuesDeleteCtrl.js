angular.module("pathianApp.controllers")
    .controller("issuesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueService",
        function($scope, $rootScope, $location, $routeParams, issueService) {
            $rootScope.global.linkpath = "#/commissioning/issues";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            issueService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/issues");
            };

            $scope.submit = function() {
                var model={
                    id:$scope.id
                };
                issueService["delete"](model, function() {
                    $location.path("/commissioning/issues");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);