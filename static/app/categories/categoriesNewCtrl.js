angular.module("pathianApp.controllers")
    .controller("categoriesNewCtrl", [
        "$scope", "$rootScope", "$location", "categoryService",
        function($scope, $rootScope, $location, categoryService) {
            $rootScope.global.linkpath = "#/commissioning/categories";

            $scope.submit = function(){
                categoryService.save($scope.model, function() {
                    $location.path("/commissioning/categories");
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
                $location.path("/commissioning/categories");
            }
        }
    ]);