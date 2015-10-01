angular.module("pathianApp.factories")
    .factory('permissionsFactory', ["$rootScope", "$http",
        function($rootScope, $http) {
            var userPermissions;
            var adminPermissions = [
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
            ];
            var commissioningPermissions = [
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
            ];
            var reportingPermissions = [
                'Upload Group Data',
                'Run Group Reports',
                'Run NAICS Reports',
                'Run SIC Reports',
                'Run Component Reports',
                'Run Subcomponent Reports',
                'Run Bronze Reports'
            ];
            return {
                setPermissions: function(permissions) {
                    userPermissions = permissions;
                },
                hasPermissions: function(neededPermissions) {
                    // no permissions specified so universal access
                    if (neededPermissions.length <= 0)
                        return true;
                    // Loop through the permissions and make sure they all match
                    for (var i=0; i < neededPermissions.length; ++i){
                        if ($.inArray(neededPermissions[i], userPermissions) === -1) {
                            return false;
                        }
                    }
                    return true;
                },
                hasAnyPermission: function(permissions) {
                    // no permissions are required
                    if (permissions.length <= 0) {
                        return true;
                    }

                    // When one permission is found return true
                    for (var i=0; i < permissions.length; i++) {
                        if ($.inArray(permissions[i], userPermissions) !== -1) {
                            return true
                        }
                    }
                    return false;
                },
                isAdmin: function() {
                    for (var i=0; i<userPermissions.length; i++) {
                        // if even one of the admin submenus is in the users permission they need to see the admin menu
                        if ($.inArray(userPermissions[i], adminPermissions) !== -1) {
                            return true;
                        }
                    }
                    return false;
                },
                canCommission: function() {
                    for (var i=0; i<userPermissions.length;i++) {
                        // if even one of the commissioning privileges is in the user permission show the menu
                        if ($.inArray(userPermissions[i], commissioningPermissions) !== -1) {
                            return true;
                        }
                    }
                    return false;
                },
                canAccessReporting: function() {
                    for (var i=0; i<userPermissions.length; i++) {
                        if ($.inArray(userPermissions[i], reportingPermissions) !== -1) {
                            return true;
                        }
                    }
                    return false;
                },
                getNewPermissions: function(user_id) {
                    // use low level $http service, as ngResource used by services expects array of objects
                    $http.get('/api/Users/' + user_id + '/Permissions').success(function(p) {
                        userPermissions = p;
                        $rootScope.global.updatePermissions();
                    });
                }
            }
        }
    ]);