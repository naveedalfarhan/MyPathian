angular.module("pathianApp.controllers")
    .controller("issuetypesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueTypeService",
        function ($scope, $rootScope, $location, $routeParams, issueTypeService) {
            $rootScope.global.linkpath = "#/admin/issuetypes";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            issueTypeService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                issueTypeService.update($scope.model, function(){
                    $location.path("/admin/issuetypes");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function(){
                $location.path("/admin/issuetypes");
            };
        }
    ]);
