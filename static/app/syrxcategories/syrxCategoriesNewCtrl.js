angular.module("pathianApp.controllers")
    .controller("syrxCategoriesNewCtrl", [
        "$scope", "$rootScope", "$location", "syrxCategoryService",
        function($scope, $rootScope, $location, syrxCategoryService) {
            $rootScope.global.linkpath = "#/admin/syrxcategories";

            $scope.submit = function(){
                syrxCategoryService.save($scope.model, function() {
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
            }
        }
    ]);