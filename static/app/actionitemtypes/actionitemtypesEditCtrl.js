angular.module("pathianApp.controllers")
    .controller("actionitemtypesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "actionitemtypeService",
        function ($scope, $rootScope, $location, $routeParams, actionitemtypeService) {
            $rootScope.global.linkpath = "#/admin/actionitemtypes";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            actionitemtypeService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                actionitemtypeService.update($scope.model, function(){
                    $location.path("/admin/actionitemtypes");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/actionitemtypes");
            };
        }
    ]);
