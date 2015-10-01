angular.module("pathianApp.controllers")
    .controller("weatherstationsDeleteCtrl", ["$scope", "$rootScope", "$routeParams", "$location", "weatherstationService",
        function ($scope, $rootScope, $routeParams, $location, weatherstationService) {
            $rootScope.global.linkpath = "#/admin/weatherstations";
            $scope.id = $routeParams.id;

            weatherstationService.get({ id: $scope.id }, function (ws) {
                $scope.model = ws;
            });
            
            $scope.cancel = function() {
                $location.path("/admin/weatherstations");
            };
            
            $scope.submit = function () {
                var group = {
                    id: $scope.id
                };
                weatherstationService["delete"](group, function () {
                    $location.path("/admin/weatherstations");
                });
            };
        }
    ]);