angular.module("pathianApp.controllers")
    .controller("projectsDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "projectService",
        function($scope, $rootScope, $location, $routeParams, projectService) {
            $rootScope.global.linkpath = "#/commissioning/projects";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            projectService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/projects");
            };

            $scope.submit = function() {
                projectService["delete"]({id:$scope.id}, function() {
                    $location.path("/commissioning/projects");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);