angular.module("pathianApp.controllers")
    .controller("actionitemstatusesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitemstatusService",
        function ($scope, $rootScope, $location, $routeParams, actionitemstatusService) {
            $rootScope.global.linkpath = "#/admin/actionitemstatuses";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            actionitemstatusService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                actionitemstatusService.update($scope.model, function(){
                    $location.path("/admin/actionitemstatuses");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

             $scope.cancel = function () {
                $location.path('/admin/actionitemstatuses');
            }
        }
    ]);
