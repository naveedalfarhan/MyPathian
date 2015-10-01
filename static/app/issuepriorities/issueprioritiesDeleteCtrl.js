angular.module("pathianApp.controllers")
    .controller("issueprioritiesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issuePriorityService",
        function ($scope, $rootScope, $location, $routeParams, issuePriorityService) {
            $rootScope.global.linkpath = "#/admin/issuepriorities";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            issuePriorityService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/issuepriorities")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                issuePriorityService["delete"](model, function(){
                   $location.path("/admin/issuepriorities");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);