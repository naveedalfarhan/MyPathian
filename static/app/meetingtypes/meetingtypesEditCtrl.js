angular.module("pathianApp.controllers")
    .controller("meetingtypesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "meetingtypeService",
        function ($scope, $rootScope, $location, $routeParams, meetingtypeService) {
            $rootScope.global.linkpath = "#/admin/meetingtypes";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            meetingtypeService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                meetingtypeService.update($scope.model, function(){
                    $location.path("/admin/meetingtypes");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/meetingtypes");
            }
        }
    ]);
