angular.module('pathianApp.controllers')
    .controller('componentsMainCtrl', ['$scope', '$rootScope', '$location',
        function($scope, $rootScope, $location) {
            $rootScope.global.linkpath = '#/admin/components';

            $scope.userPermissions = $rootScope.global.userPermissions;
        }
    ]);