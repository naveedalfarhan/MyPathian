angular.module("pathianApp.controllers")
    .controller("actionitemprioritiesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitempriorityService",
        function ($scope, $rootScope, $location, $routeParams, actionitempriorityService) {
            $rootScope.global.linkpath = "#/admin/actionitempriorities";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            actionitempriorityService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/actionitempriorities")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                actionitempriorityService["delete"](model, function(){
                   $location.path("/admin/actionitempriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);