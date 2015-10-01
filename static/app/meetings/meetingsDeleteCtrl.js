angular.module("pathianApp.controllers")
    .controller("meetingsDeleteCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "meetingService",
        function($scope, $rootScope, $routeParams, $location, meetingService) {
            $rootScope.global.linkpath = "#/commissioning/meetings";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            meetingService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/meetings");
            };

            $scope.submit = function() {
                var model={
                    id:$scope.id
                };
                meetingService["delete"](model, function() {
                    $location.path("/commissioning/meetings");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);