angular.module("pathianApp.controllers")
    .controller("weatherstationsEditCtrl", ["$scope", "$rootScope", "$routeParams", "$location", "weatherstationService",
        function ($scope, $rootScope, $routeParams, $location, weatherstationService) {
            $rootScope.global.linkpath = "#/admin/weatherstations";
            $scope.id = $routeParams.id;

            weatherstationService.get({ id: $scope.id }, function(ws) {
                $scope.model = ws;
            });

            $scope.submit = function () {
                weatherstationService.update($scope.model, function () {
                    $location.path("/admin/weatherstations");
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/weatherstations");
            }
        }
    ]);