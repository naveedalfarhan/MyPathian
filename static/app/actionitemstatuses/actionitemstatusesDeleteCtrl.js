angular.module("pathianApp.controllers")
    .controller("actionitemstatusesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitemstatusService",
        function ($scope, $rootScope, $location, $routeParams, actionitemstatusService) {
            $rootScope.global.linkpath = "#/admin/actionitemstatuses";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            actionitemstatusService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/actionitemstatuses")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                actionitemstatusService["delete"](model, function(){
                   $location.path("/admin/actionitemstatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);