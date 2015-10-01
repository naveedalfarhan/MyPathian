if (!('map' in Array.prototype)) {
    Array.prototype.map = function (mapper, that /*opt*/) {
        var other = new Array(this.length);
        for (var i = 0, n = this.length; i < n; i++)
            if (i in this)
                other[i] = mapper.call(that, this[i], i, this);
        return other;
    };
}
if (!Array.prototype.filter) {
  Array.prototype.filter = function(fun/*, thisArg*/) {
    'use strict';

    if (this === void 0 || this === null) {
      throw new TypeError();
    }

    var t = Object(this);
    var len = t.length >>> 0;
    if (typeof fun !== 'function') {
      throw new TypeError();
    }

    var res = [];
    var thisArg = arguments.length >= 2 ? arguments[1] : void 0;
    for (var i = 0; i < len; i++) {
      if (i in t) {
        var val = t[i];

        // NOTE: Technically this should Object.defineProperty at
        //       the next index, as push can be affected by
        //       properties on Object.prototype and Array.prototype.
        //       But that method's new, and collisions should be
        //       rare, so use the more-compatible alternative.
        if (fun.call(thisArg, val, i, t)) {
          res.push(val);
        }
      }
    }

    return res;
  };
}
angular.module("pathianApp.controllers", []);
angular.module("pathianApp.directives", []);
angular.module("pathianApp.factories", []);
angular.module("pathianApp.services", []);
angular.module("pathianApp.routes", []);
angular.module("pathianApp.interceptor", []);
var app = angular.module("pathianApp", // declare this module, named "pathianApp". Matches ng-app attribute on index page.
    [
        "lr.upload",
        "blueimp.fileupload",
        "pathianApp.controllers",
		"pathianApp.directives",
        "ngRoute",                  // declare the modules that pathianApp depends on
        "ngResource",
        "ngDragDrop",
        "ngSanitize",
        "kendo.directives",
        "ui.bootstrap",
        "toaster",


        "pathianApp.directives",
        "pathianApp.controllers",
        "pathianApp.factories",
        "pathianApp.services",
        "pathianApp.routes",
        "pathianApp.interceptor"
    ]);

app.filter('withCategory', function() {
    return function(items, category) {
        var out = [];
        for (var i = 0; i < items.length; i++) {
            if(items[i].category_name === category){
                out.push(items[i]);
            }
        }
        return out;
    };
});

app.filter('withComponent', function() {
    return function(items, component) {
        var out = [];
        for (var i = 0; i < items.length; i++) {
            if(items[i].component_full_name === component){
                out.push(items[i]);
            }
        }
        return out;
    };
});

app.run(["$rootScope", "$http", "$location", "$modal", "$route", "permissionsFactory", "userReportingGroupService",
    function ($rootScope, $http, $location, $modal, $route, permissionsFactory, userReportingGroupService) {
        console.log("run");
        $rootScope.global = $rootScope.global || {};


        // initialize the permission scheme
        $rootScope.global.userPermissions = {};

        $rootScope.global.updatePermissions = function() {
            $rootScope.global.userPermissions = {
                'isAdmin': permissionsFactory.isAdmin(),
                'canCommission': permissionsFactory.canCommission(),
                'canAccessReporting': permissionsFactory.canAccessReporting(),
                'users': permissionsFactory.hasAnyPermission(['Manage Users', 'View Users']),
                'roles': permissionsFactory.hasAnyPermission(['Manage Roles', 'View Roles']),
                'weatherstations': permissionsFactory.hasAnyPermission(['Manage Weather Stations', 'View Weather Stations']),
                'groups': permissionsFactory.hasAnyPermission(['Manage Groups', 'View Groups']),
                'accounts': permissionsFactory.hasAnyPermission(['Manage Accounts', 'View Accounts']),
                'components': permissionsFactory.hasAnyPermission(["Manage Component Structure Tree" ,
                                                                    "View Component Structure Tree" ,
                                                                    "Manage Component Mapping Tree" ,
                                                                    "View Component Mapping Tree" ,
                                                                    "Manage Component Points" ,
                                                                    "View Component Points" ,
                                                                    "Manage Component Engineering" ,
                                                                    "View Component Engineering"]),
                'componentStructureTree': permissionsFactory.hasAnyPermission(['View Component Structure Tree', 'Manage Component Structure Tree']),
                'componentMappingTree': permissionsFactory.hasAnyPermission(['View Component Mapping Tree', 'Manage Component Mapping Tree']),
                'componentPointManager': permissionsFactory.hasAnyPermission(['View Component Points', 'Manage Component Points']),
                'componentEngineering': permissionsFactory.hasAnyPermission(['View Component Engineering', 'Manage Component Engineering']),
                'meetingTypes': permissionsFactory.hasAnyPermission(['Manage Meeting Types', 'View Meeting Types']),
                'utilityCompanies': permissionsFactory.hasAnyPermission(['Manage Utility Companies', 'View Utility Companies']),
                'actionItemPriorities': permissionsFactory.hasAnyPermission(['Manage Action Item Priorities', 'View Action Item Priorities']),
                'actionItemStatuses': permissionsFactory.hasAnyPermission(['Manage Action Item Statuses', 'View Action Item Statuses']),
                'actionItemTypes': permissionsFactory.hasAnyPermission(['Manage Action Item Types', 'View Action Item Types']),
                'taskPriorities': permissionsFactory.hasAnyPermission(['Manage Task Priorities', 'View Task Priorities']),
                'taskStatuses': permissionsFactory.hasAnyPermission(['Manage Task Statuses', 'View Task Statuses']),
                'taskTypes': permissionsFactory.hasAnyPermission(['Manage Task Types', 'View Task Types']),
                'issuePriorities': permissionsFactory.hasAnyPermission(['Manage Issue Priorities', 'View Issue Priorities']),
                'issueStatuses': permissionsFactory.hasAnyPermission(['Manage Issue Statuses', 'View Issue Statuses']),
                'issueTypes': permissionsFactory.hasAnyPermission(['Manage Issue Types', 'View Issue Types']),
                'equipment': permissionsFactory.hasAnyPermission(['Manage Equipment', 'View Equipment']),
                'categories': permissionsFactory.hasAnyPermission(['Manage Categories', 'View Categories']),
                'contacts': permissionsFactory.hasAnyPermission(['Manage Contacts', 'View Contacts']),
                'tasks': permissionsFactory.hasAnyPermission(['Manage Tasks', 'View Tasks']),
                'issues': permissionsFactory.hasAnyPermission(['Manage Issues', 'View Issues']),
                'projects': permissionsFactory.hasAnyPermission(['Manage Projects', 'View Projects']),
                'eco': permissionsFactory.hasAnyPermission(['Manage ECO', 'View ECO']),
                'committees': permissionsFactory.hasAnyPermission(['Manage Committees', 'View Committees']),
                'meetings': permissionsFactory.hasAnyPermission(['Manage Meetings', 'View Meetings']),
                'uploadGroupData': permissionsFactory.hasAnyPermission(['Upload Group Data']),
                'uploadGroupDataDivider': permissionsFactory.hasAnyPermission(['Upload Group Data']) &&
                    permissionsFactory.hasAnyPermission(['Run Group Reports', 'Run NAICS Reports', 'Run SIC Reports']),
                'runGroupReports': permissionsFactory.hasAnyPermission(['Run Group Reports']),
                'runNaicsReports': permissionsFactory.hasAnyPermission(['Run NAICS Reports']),
                'runSicReports': permissionsFactory.hasAnyPermission(['Run SIC Reports']),
                'runEquipmentSyrxReports': permissionsFactory.hasAnyPermission(['Run Equipment Syrx Reports']),
                'runReportDivider': permissionsFactory.hasAnyPermission(['Run Group Reports', 'Run NAICS Reports', 'Run SIC Reports']) &&
                    permissionsFactory.hasAnyPermission(['Run Component Reports', 'Run Subcomponent Reports']),
                'runComponentReports': permissionsFactory.hasAnyPermission(['Run Component Reports']),
                'runSubcomponentReports': permissionsFactory.hasAnyPermission(['Run Subcomponent Reports']),
                'dashboard': permissionsFactory.hasPermissions(['View Dashboard']),
                'componentReportsDivider': permissionsFactory.hasPermissions(['Run Bronze Reports']) &&
                    permissionsFactory.hasAnyPermission(['Run Component Reports', 'Run Subcomponent Reports']),
                'runBronzeReports': permissionsFactory.hasPermissions(['Run Bronze Reports']),
                'viewReportingData': permissionsFactory.hasPermissions(['View Reporting Data']),
                'runPointDataReport': permissionsFactory.hasPermissions(['Run Point Data Report'])
            };
        };

        $rootScope.$on('permissionsChanged', function() {
            if ($rootScope.global.user && $rootScope.global.user.id) {
                permissionsFactory.getNewPermissions($rootScope.global.user.id);
            }
        });

        var response = $.ajax({
            type: "GET",
            url: "/api/Login",
            async: false
        });

        if (response.status != 200) {
            $rootScope.global.user = null;
            permissionsFactory.setPermissions([]);
        }
        else {
            var res = JSON.parse(response.responseText);
            $rootScope.global.user = res;
            $rootScope.global.reportingGroup = res.reporting_group;
            permissionsFactory.setPermissions(res.permissions);
            $rootScope.global.updatePermissions();
            $rootScope.global.reportingGroup = res.reporting_group;
        }

        $rootScope.$on("$routeChangeStart", function(scope, next, current) {
            var path = $location.path();
            if (!$rootScope.global.user && path != "" && path != "/" && path != "/home" && path != "/login" && path.substring(0, 7) != "/bronze")
                $location.path("/home");
            var route = next.$$route;

            if (!route)
                return;

            var nextPermissions = route.permissions;
            if (nextPermissions.length < 1)
                return;
            // Check if the user has any of the permissions....this can be easily changed later
            if (!permissionsFactory.hasAnyPermission(nextPermissions)) {
                $location.path("/forbidden");
            }
        });

        $rootScope.global.logout = function () {
            $http["delete"]("/api/Login")
                .then(function() {
                    $rootScope.global.user = null;
                    $rootScope.global.reportingGroup = null;
                    permissionsFactory.setPermissions([]);
                    $rootScope.global.updatePermissions();
                    $location.path("/home");
                });
        };

        $rootScope.global.reportingGroupTreeOptions = {
                            dataTextField: "name",
                            dataSource: {
                                transport: {
                                    read: {
                                        url: "/api/groups/getChildrenOf",
                                        dataType: "json"
                                    }
                                },
                                schema: {
                                    model: {
                                        id: "id",
                                        hasChildren: "childIds.length > 0"
                                    }
                                }
                            }
                        };

        $rootScope.global.changeReportingGroup = function() {
            var modalWindow = $modal.open({
                templateUrl: "/static/app/changeReportingGroup.html",
                backdrop: "static",
                controller: ["$scope",
                    function($scope) {
                        $scope.model = {
                            group: $rootScope.global.reportingGroup
                        };

                        $scope.reportingGroupTreeOptions = {
                            dataTextField: "name",
                            dataSource: {
                                transport: {
                                    read: {
                                        url: "/api/groups/getChildrenOf",
                                        dataType: "json"
                                    }
                                },
                                schema: {
                                    model: {
                                        id: "id",
                                        hasChildren: "childIds.length > 0"
                                    }
                                }
                            }
                        };

                        $scope.componentStructureTree = {
                            template: "#=item.num# #=item.description#",
                            dataSource: {
                                transport: {
                                    read: {
                                        url: "/api/components/getStructureChildrenOf",
                                        dataType: "json"
                                    }
                                },
                                schema: {
                                    model: {
                                        id: "id",
                                        hasChildren: "structure_child_ids.length > 0"
                                    }
                                }
                            }
                        };

                        $scope.cancel = function() {
                            modalWindow.close();
                        };
                        $scope.submit = function() {
                            $rootScope.global.reportingGroup = $scope.model.group;
                            userReportingGroupService.updateReportingGroup({group_id: $scope.model.group.id});
                            modalWindow.close();
                        };
                    }
                ]
            });
        };
        
        // Valid types for model fields are "string", "number", "boolean", "date"
        $rootScope.global.getJsonGridOptions = function (parameters) {
            /// <summary>This function gets an object containing settings for a Kendo grid
            /// through angular.</summary>
            /// <param name="controllerName" type="string">The name of the REST endpoint (controller)</param>
            /// <param name="model" type="object">A complex object containing the model definition of the data
            /// that will be returned by a GET call to the REST endpoint.</param>
            /// <param name="columns" type="object">A complex object containing the column definition for display
            /// in the grid.</param>
            /// <param name="editable" type="object">A value indicating the type of editing the grid will support.
            /// Options include "incell", "inline", "popup" and false. "inline" is selected by default.</param>
            /// <param name="editable" type="string">An optionan custom template for the create button.</param>

            var options = {
                scrollable: false,
                filterable: true,
                sortable: { mode: "multiple" },
                pageable: true,
                toolbar: parameters.createTemplate === undefined ?
                    ["create"]
                    : (parameters.createTemplate === false ? false : [{ template: parameters.createTemplate }]),
                columns: parameters.columns,
                editable: parameters.editable === undefined ? "inline" : parameters.editable
            };

            if (parameters.other !== undefined) {
                for (var k in parameters.other)
                    options[k] = parameters.other[k];
            }

            return {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/" + parameters.controllerName,
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        update: {
                            url: function (options) {
                                return "/api/" + parameters.controllerName + "/" + options.id;
                            },
                            dataType: "json",
                            contentType: "application/json",
                            type: "PUT"
                        },
                        destroy: {
                            url: function (options) {
                                return "/api/" + parameters.controllerName + "/" + options.id;
                            },
                            dataType: "json",
                            contentType: "application/json",
                            type: "DELETE"
                        },
                        create: {
                            url: "/api/" + parameters.controllerName,
                            dataType: "json",
                            contentType: "application/json",
                            type: "POST"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    schema: {
                        data: function (response) {
                            return response.data;
                        },
                        total: function (response) {
                            return response.total;
                        },
                        model: parameters.model
                    },
                    pageSize: 10,
                    serverPaging: true,
                    serverFiltering: true,
                    serverSorting: true,
                    sort: parameters.defaultSort
                },
                options: options
            };
        };

        $("body").show();
    }
]);
