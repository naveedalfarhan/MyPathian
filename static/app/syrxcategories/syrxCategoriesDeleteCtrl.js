angular.module("pathianApp.controllers")
    .controller("syrxCategoriesDeleteCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "syrxCategoryService",
        function($scope, $rootScope, $routeParams, $location, syrxCategoryService){
            $rootScope.global.linkpath = "#/api/syrxcategories";
            $scope.id = $routeParams.id;

            syrxCategoryService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.cancel = function() {
                $location.path("/admin/syrxcategories");
            };

            $scope.submit = function(){
                var model = {
                    id:$scope.id
                };
                syrxCategoryService["delete"](model, function(){
                    $location.path("/admin/syrxcategories");
                });
            };
        }
    ]);