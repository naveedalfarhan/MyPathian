angular.module("pathianApp.controllers")
    .controller("weatherstationsNewCtrl", ["$scope", "$rootScope", "$location", "weatherstationService",
        function ($scope, $rootScope, $location, weatherstationService) {
            $rootScope.global.linkpath = "#/admin/weatherstations";
            
            $scope.submit = function () {
                weatherstationService.save($scope.model, function () {
                    $location.path("/admin/weatherstations");
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/weatherstations");
            }
        }
    ]);