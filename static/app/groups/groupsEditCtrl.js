angular.module("pathianApp.controllers")
    .controller("groupsEditCtrl", ["$scope", "$rootScope", "$routeParams", "$location", "groupService", "weatherstationService", 'naicsService', 'sicService',
        function ($scope, $rootScope, $routeParams, $location, groupService, weatherstationService, naicsService, sicService) {
            $rootScope.global.linkpath = "#/admin/groups";
            $scope.id = $routeParams.id;
            $scope.weatherstations = weatherstationService.list();

            groupService.get({ id: $scope.id }, function(model) {
                $scope.model = model;
            });

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
            };
        }
    ]);