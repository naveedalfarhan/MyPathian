angular.module("pathianApp.controllers")
    .controller("taskstatusesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "taskStatusService",
        function ($scope, $rootScope, $location, $routeParams, taskStatusService) {
            $rootScope.global.linkpath = "#/admin/taskstatuses";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            taskStatusService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                taskStatusService.update($scope.model, function(){
                    $location.path("/admin/taskstatuses");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

             $scope.cancel = function () {
                $location.path('/admin/taskstatuses');
            }

        }
    ]);
