angular.module("pathianApp.controllers")
    .controller("taskstatusesDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskStatusService",
        function ($scope, $rootScope, $location, $routeParams, taskStatusService) {
            $rootScope.global.linkpath = "#/admin/taskstatuses";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            taskStatusService.get({ id: $scope.id }, function(model){
                $scope.model = model;
            });

            $scope.cancel = function(){
                $location.path("/admin/taskstatuses")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                taskStatusService["delete"](model, function(){
                   $location.path("/admin/taskstatuses");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

        }
    ]);