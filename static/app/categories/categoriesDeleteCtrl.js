angular.module("pathianApp.controllers")
    .controller("categoriesDeleteCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "categoryService",
        function($scope, $rootScope, $routeParams, $location, categoryService){
            $rootScope.global.linkpath = "#/commissioning/categories";
            $scope.id = $routeParams.id;

            categoryService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/commissioning/categories");
            };

            $scope.submit = function(){
                var model = {
                    id:$scope.id
                };
                categoryService["delete"](model, function(){
                    $location.path("/commissioning/categories");
                });
            };
        }
    ]);