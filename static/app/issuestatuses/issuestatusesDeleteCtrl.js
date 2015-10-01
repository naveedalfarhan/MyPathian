angular.module("pathianApp.controllers")
    .controller("issuestatusesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueStatusService",
        function ($scope, $rootScope, $location, $routeParams, issueStatusService) {
            $rootScope.global.linkpath = "#/admin/issuestatuses";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            issueStatusService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/issuestatuses")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                issueStatusService["delete"](model, function(){
                   $location.path("/admin/issuestatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };
        }
    ]);