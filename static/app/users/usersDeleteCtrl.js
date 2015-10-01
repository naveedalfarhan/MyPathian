angular.module("pathianApp.controllers")
    .controller("usersDeleteCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "userService",
        function($scope, $rootScope, $routeParams, $location, userService) {
            $rootScope.global.linkpath = "#/admin/users";
            $scope.id = $routeParams.id;

            userService.get({ id: $scope.id }, function(user) {
                $scope.username = user.username;
            });

            $scope.cancel = function() {
                $location.path("/admin/users");
            };

            $scope.submit = function() {
                var user = {
                    id: $scope.id
                };
                userService["delete"](user, function() {
                    $location.path("/admin/users");
                });
            };
        }
    ]);