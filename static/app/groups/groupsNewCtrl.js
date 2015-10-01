angular.module("pathianApp.controllers")
    .controller("groupsNewCtrl", ["$scope", "$rootScope", "$location", "groupService", "weatherstationService", "naicsService", "sicService",
        function ($scope, $rootScope, $location, groupService, weatherstationService, naicsService, sicService) {
            $rootScope.global.linkpath = "#/admin/groups";
            $scope.weatherstations = weatherstationService.list();

            $scope.model = {
                'name': undefined,
                'weatherstation_id': undefined,
                'first_name': undefined,
                'last_name': undefined,
                'job_title': undefined,
                'email': undefined,
                'address': undefined,
                'city': undefined,
                'state': undefined,
                'zip': undefined,
                'naics_code': undefined,
                'sic_code': undefined
            };

            $scope.naicsCodes = naicsService.getLevelFive(function() {
            });

            $scope.sicCodes = sicService.getLevelTwo(function() {
            });
            
            $scope.submit = function () {
                groupService.save($scope.model, function () {
                    $location.path("/admin/groups");
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/groups");
            }
        }
    ]);