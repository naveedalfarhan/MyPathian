angular.module("pathianApp.controllers")
    .controller("categoriesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "categoryService",
        function($scope, $rootScope, $location, $routeParams, categoryService) {
            $rootScope.global.linkpath = "#/commissioning/categories";
            $scope.id = $routeParams.id;

            categoryService.get({id:$scope.id}, function(model) {
                $scope.model = model;
            });

            $scope.submit = function() {
                categoryService.update($scope.model, function() {
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