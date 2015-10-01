angular.module("pathianApp.controllers")
    .controller("issueprioritiesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issuePriorityService",
        function ($scope, $rootScope, $location, $routeParams, issuePriorityService) {
            $rootScope.global.linkpath = "#/admin/issuepriorities";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            issuePriorityService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function(){
                issuePriorityService.update($scope.model, function(){
                    $location.path("/admin/issuepriorities");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/issuepriorities");
            };
        }
    ]);
