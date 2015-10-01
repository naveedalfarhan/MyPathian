angular.module("pathianApp.controllers")
    .controller("rolesEditCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "roleService",
    function($scope, $rootScope, $routeParams, $location, roleService) {
        $rootScope.global.linkpath = "#/admin/roles";
        $scope.id = $routeParams.id;

        roleService.get({ id: $scope.id }, function(role) {
            $scope.name = role.name;
            $scope.rolePermissions = role.permissions;
        });

        $scope.permissions = [
            'Manage Users',
            'View Users',
            'Manage Roles',
            'View Roles',
            'Manage Weather Stations',
            'View Weather Stations',
            'Manage Groups',
            'View Groups',
            'Manage Group Mappings',
            'View Group Mappings',
            'Manage Accounts',
            'View Accounts',
            'Manage Component Structure Tree',
            'View Component Structure Tree',
            'Manage Component Mapping Tree',
            'View Component Mapping Tree',
            'Manage Component Points',
            'View Component Points',
            'Manage Component Engineering',
            'View Component Engineering',
            'Manage Meeting Types',
            'View Meeting Types',
            'Manage Utility Companies',
            'View Utility Companies',
            'Manage Action Item Priorities',
            'View Action Item Priorities',
            'Manage Action Item Types',
            'View Action Item Types',
            'Manage Action Item Statuses',
            'View Action Item Statuses',
            'Manage Task Priorities',
            'View Task Priorities',
            'Manage Task Statuses',
            'View Task Statuses',
            'Manage Task Types',
            'View Task Types',
            'Manage Issue Priorities',
            'View Issue Priorities',
            'Manage Issue Statuses',
            'View Issue Statuses',
            'Manage Issue Types',
            'View Issue Types',
            'Manage Equipment',
            'View Equipment',
            'Manage Categories',
            'View Categories',
            'Manage Contacts',
            'View Contacts',
            'Manage Tasks',
            'View Tasks',
            'Manage Issues',
            'View Issues',
            'Manage Projects',
            'View Projects',
            'Manage ECO',
            'View ECO',
            'Manage Committees',
            'View Committees',
            'Manage Meetings',
            'View Meetings',
            'Upload Group Data',
            'Run Group Reports',
            'Run NAICS Reports',
            'Run SIC Reports',
            'Run Equipment Syrx Reports',
            'Run Component Reports',
            'Run Subcomponent Reports',
            'Run Bronze Reports',
            'Run Point Data Report',
            'View Dashboard',
            'Manage Reset Schedules',
            "View Reset Schedules",
            'View Reporting Data'
        ];

        $scope.toggleSelection = function(permission) {
            var index = $scope.rolePermissions.indexOf(permission);

            // permission is currently selected
            if (index > -1){
                // removes the permission from the list of selected permissions
                $scope.rolePermissions.splice(index,1);
            } else {
                // add the permission to the list of selected permissions
                $scope.rolePermissions.push(permission);
            }
        };

        $scope.submit = function() {
            var role = {
                id: $scope.id,
                name: $scope.name,
                permissions: $scope.rolePermissions
            };
            console.log(role);
            roleService.update(role, function() {
                // rebuild permissions for user in case they were in the role that changed
                $rootScope.$broadcast("permissionsChanged");
                $location.path("/admin/roles");
            }, function(e) {
                $scope.message = e.data.message;
                $scope.showErrorMessage = true;
            });
        };

        $scope.cancel = function () {
            $location.path("/admin/roles");
        }
    }
]);