angular.module("pathianApp.controllers")
    .controller("actionitemtypesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitemtypeService",
        function ($scope, $rootScope, $location, $routeParams, actionitemtypeService) {
            $rootScope.global.linkpath = "#/admin/actionitemtypes";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            actionitemtypeService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/actionitemtypes")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                actionitemtypeService["delete"](model, function(){
                   $location.path("/admin/actionitemtypes");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);