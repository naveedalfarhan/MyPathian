angular.module("pathianApp.controllers")
    .controller("equipmentDeleteCtrl", ["$scope", "$rootScope", "$routeParams", "$location", "equipmentService", "toaster",
        function ($scope, $rootScope, $routeParams, $location, equipmentService, toaster) {
            $rootScope.global.linkpath = "#/commissioning/equipment";
            $scope.id = $routeParams.id;

            equipmentService.get({ id: $scope.id }, function (model) {
                $scope.model = model;
            });
            
            $scope.cancel = function() {
                $location.path("/commissioning/equipment");
            };
            
            $scope.submit = function () {
                var model = {
                    id: $scope.id
                };
                equipmentService["delete"](model, function () {
                    toaster.pop('success', "Delete", "Equipment deleted.");
                    $location.path("/commissioning/equipment");
                }, function(httpResponse){
                    toaster.pop('error', "Delete Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                });
            };
        }
    ]);