angular.module("pathianApp.controllers")
    .controller("rolesDeleteCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "roleService",
        function($scope, $rootScope, $routeParams, $location, roleService) {
            $rootScope.global.linkpath = "#/admin/roles";
            $scope.id = $routeParams.id;

            roleService.get({ id: $scope.id }, function(role) {
                $scope.name = role.name;
            });

            $scope.cancel = function() {
                $location.path("/admin/roles");
            };

            $scope.submit = function() {
                var role = {
                    id: $scope.id
                };
                roleService["delete"](role, function() {
                    $location.path("/admin/roles");
                });
            };
        }
    ]);