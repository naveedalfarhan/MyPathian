angular.module("pathianApp.controllers")
    .controller("issuestatusesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueStatusService",
        function ($scope, $rootScope, $location, $routeParams, issueStatusService) {
            $rootScope.global.linkpath = "#/admin/issuestatuses";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            issueStatusService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                issueStatusService.update($scope.model, function(){
                    $location.path("/admin/issuestatuses");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/issuestatuses");
            };
        }
    ]);
