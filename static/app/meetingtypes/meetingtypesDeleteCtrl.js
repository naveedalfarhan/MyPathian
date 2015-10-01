angular.module("pathianApp.controllers")
    .controller("meetingtypesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "meetingtypeService",
        function ($scope, $rootScope, $location, $routeParams, meetingtypeService) {
            $rootScope.global.linkpath = "#/admin/meetingtypes";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            meetingtypeService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/meetingtypes")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                meetingtypeService["delete"](model, function(){
                   $location.path("/admin/meetingtypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);