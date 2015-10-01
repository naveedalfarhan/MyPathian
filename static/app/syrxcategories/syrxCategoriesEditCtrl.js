angular.module("pathianApp.controllers")
    .controller("syrxCategoriesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "syrxCategoryService",
        function($scope, $rootScope, $location, $routeParams, syrxCategoryService) {
            $rootScope.global.linkpath = "#/admin/syrxcategories";
            $scope.id = $routeParams.id;

            syrxCategoryService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function() {
                syrxCategoryService.update($scope.model, function() {
                    $location.path("/admin/syrxcategories");
                }, function(e) {
                    switch(e.status){
                        case 401:
                            $location.path("/login")
                            break;
                        case 409:
                            $scope.message = "A category with that name already exists.";
                            break;
                    }
                });
            };

            $scope.cancel = function () {
                $location.path("/admin/syrxcategories");
            };
        }
    ]);