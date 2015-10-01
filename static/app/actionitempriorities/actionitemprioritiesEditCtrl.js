angular.module("pathianApp.controllers")
    .controller("actionitemprioritiesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitempriorityService",
        function ($scope, $rootScope, $location, $routeParams, actionitempriorityService) {
            $rootScope.global.linkpath = "#/admin/actionitempriorities";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            actionitempriorityService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                actionitempriorityService.update($scope.model, function(){
                    $location.path("/admin/actionitempriorities");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
              $location.path("/admin/actionitempriorities");
            };
        }
    ]);
