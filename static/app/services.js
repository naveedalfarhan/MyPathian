angular.module("pathianApp.services")
    .factory("pointManagementService", ["$modal", "$http", "componentPointService",
        function($modal, $http, componentPointService) {
            return {
                launchPointEditor: function(point, componentId, callback) {
                    var mode = point ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/components/pointEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.mode = mode;
                                $innerScope.caption = mode == "edit" ? "Edit Point" : "Add Point";
                                $innerScope.viewModel = {
                                    formulaDirty: mode == "create",
                                    points: componentPointService.getByComponent({component_id: componentId})
                                };

                                $innerScope.pointTypes = [
                                    {value: "EP", name: "Energy Point"},
                                    {value: "CP", name: "Calculated Point"},
                                    {value: "PP", name: "Position Point"},
                                    {value: "NP", name: "Numeric Point"},
                                    {value: "BP", name: "Binary Point"}
                                ];

                                $innerScope.unitTypes = [
                                    {value:"kW", name: "kW"},
                                    {value:"kWh", name: "kWh"},
                                    {value:"F", name: "degrees F"},
                                    {value:"in H20", name: "in H20"},
                                    {value:"psig", name: "psig"},
                                    {value:"cfm", name: "cfm"},
                                    {value:"lb/hr", name: "lb/hr"},
                                    {value:"gpm", name: "gpm"},
                                    {value:"cf/hr", name: "cf/hr"},
                                    {value:"gal", name: "gal"},
                                    {value:"hz", name: "hz"},
                                    {value:"rpm", name: "rpm"},
                                    {value:"%", name: "%"},
                                    {value:"Btu/lb", name: "Btu/lb"},
                                    {value:"Btuh", name: "Btuh"},
                                    {value:"$", name: "$"},
                                    {value:"kw/ton", name: "kw/ton"},
                                    {value:"lb/hr/ton", name: "lb/hr/ton"},
                                    {value:"Btuh/ton", name: "Btuh/ton"},
                                    {value:"fthd", name: "fthd"},
                                    {value:"hp", name: "hp"},
                                    {value:"Btuh/cfmd", name: "Btuh/cfmd"},
                                    {value:"kwh/cfmd", name: "kwh/cfmd"},
                                    {value:"cfm/cfmd", name: "cfm/cfmd"},
                                    {value:"cfmd", name: "cfmd"},
                                    {value:"Btuhd", name: "Btuhd"},
                                    {value:"Btuh/Btuhd", name: "Btuh/Btuhd"},
                                    {value:"kwh/cfm", name: "kwh/cfm"},
                                    {value:"tons", name: "tons"},
                                    {value:"amps", name: "amps"}
                                ];

                                $innerScope.model = point ? angular.extend({}, point) : {};

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.validateFormula = function() {
                                    $innerScope.formulaValidationError = null;
                                    componentPointService.parseFormula({}, {formula: $innerScope.model.formula},
                                        function(data) {
                                            $innerScope.viewModel.formulaDirty = false;
                                            $innerScope.model.parameters = _.map(data.identifier_names, function(name) { return {name: name}; });
                                        },
                                        function(response) {
                                            $innerScope.formulaValidationError = response.data;
                                            var message = "Unexpected formula error";
                                            if (response.data.exception_type == "InvalidTokenException") {
                                                message = "Formula error: invalid token at character " + (response.data.position + 1);
                                            } else if (response.data.exception_type == "InvalidExpressionException") {
                                                message = "Formula error: expecting expression at ";
                                                if (response.data.end)
                                                    message += " end";
                                                else
                                                    message += " character " + (response.data.position + 1);
                                            }
                                            $innerScope.formulaValidationError.message = message;
                                            $innerScope.viewModel.formulaDirty = true;
                                        }
                                    )
                                };

                                $innerScope.submit = function() {
                                    // make sure that code is entered
                                    if (!$innerScope.model.code) {
                                        alert('Code is required.');
                                        return false;
                                    }
                                    if ($innerScope.model.id) {
                                        componentPointService.update({
                                            component_id: componentId,
                                            point_id: $innerScope.model.id
                                        }, $innerScope.model, function () {
                                            modalWindow.close();
                                            callback();
                                        }, function(err) {
                                            alert(err.data.message);
                                        });
                                    } else {
                                        componentPointService.insert({
                                            component_id: componentId
                                        }, $innerScope.model, function () {
                                            modalWindow.close();
                                            callback();
                                        }, function(err) {
                                            alert(err.data.message);
                                        });
                                    }
                                };
                            }
                        ]
                    });
                },
                launchDeletePointConfirmation: function(point, componentId, callback) {
                    var modalWindow = $modal.open({
                        templateUrl: "/static/app/components/pointDeleteTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.model = point;

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    componentPointService.delete({
                                        component_id: componentId,
                                        point_id: $innerScope.model.id
                                    }, function () {
                                        modalWindow.close();
                                        callback();
                                    });
                                };
                            }
                        ]
                    });
                },
                setMasterPoint: function(point, componentId, callback) {
                    // sets the components reporting point equal to the current point
                    $http.post("/api/components/" + componentId + "/master_point", point)
                        .success(function() {
                            callback()
                        });
                }
            }
        }
    ])
    .factory("paragraphManagementService", ["$modal", "componentService", "syrxCategoryService", "toaster",
        function($modal, componentService, syrxCategoryService, toaster) {
            return {
                launchParagraphEditor: function(paragraph, componentId, callback) {
                    var mode = paragraph ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/components/paragraphEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                syrxCategoryService.GetAll().$promise.then(function(syrxCategories) {
                                    $innerScope.mode = mode;
                                    $innerScope.caption = mode == "edit" ? "Edit Paragraph" : "Add Paragraph";

                                    $innerScope.paragraphTypes = [
                                        {value: "AR", name: "Acceptance Requirement"},
                                        {value: "CR", name: "Commissioning Requirement"},
                                        {value: "CS", name: "Control Sequence"},
                                        {value: "DR", name: "Demand Response"},
                                        {value: "FT", name: "Functional Tests"},
                                        {value: "LC", name: "Load Curtailment"},
                                        {value: "MR", name: "Maintenance Requirements"},
                                        {value: "PR", name: "Project Requirements"},
                                        {value: "RR", name: "Roles and Responsibilities"}
                                    ];

                                    $innerScope.syrxCategories = syrxCategories;

                                    $innerScope.model = paragraph ? angular.extend({}, paragraph) : {};

                                    $innerScope.cancel = function() {
                                        modalWindow.close();
                                    };

                                    $innerScope.submit = function() {
                                        $innerScope.model.component_id = componentId;
                                        if (!$innerScope.model.id)
                                            $innerScope.model.id = 0;
                                        componentService.addParagraph({}, $innerScope.model, function () {
                                            modalWindow.close();
                                            toaster.pop('success', "Paragraph Saved.", "Paragraph Saved Successfully");
                                            callback();
                                        });
                                    };
                                });
                            }
                        ]
                    });
                },
                launchDeleteParagraphConfirmation: function(paragraph, componentId, callback) {
                    var modalWindow = $modal.open({
                        templateUrl: "/static/app/components/paragraphDeleteTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.model = paragraph;

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    componentService.deleteParagraph({
                                        id: $innerScope.model.id
                                    }, function () {
                                        modalWindow.close();
                                        callback();
                                    });
                                };
                            }
                        ]
                    });
                }
            }
        }
    ])
    .factory("componentTaskManagementService", ["$modal", "componentService", "toaster",
        function($modal, componentService, toaster) {
            return {
                launchComponentTaskEditor: function(task, componentId, taskData, callback) {
                    var mode = task ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/components/componentTaskEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.forms = {};
                                $innerScope.mode = mode;
                                $innerScope.caption = mode == "edit" ? "Edit Task" : "Add Task";
                                $innerScope.viewModel = {
                                    priorities: taskData.priorities,
                                    statuses: taskData.statuses,
                                    types: taskData.types
                                };

                                $innerScope.model = task ? angular.extend({}, task) : {};

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    if ($innerScope.forms.taskForm.$valid) {
                                        if ($innerScope.model.id) {
                                            componentService.updateComponentTask({
                                                component_id: componentId,
                                                component_task_id: $innerScope.model.id
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Task Updated.");
                                                callback();
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Task Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        } else {
                                            $innerScope.model.component_id = componentId;

                                            componentService.insertComponentTask({
                                                component_id: componentId
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Task Created.");
                                                callback();
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Task Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        }
                                    }
                                };
                            }
                        ]
                    });
                },
                launchDeleteComponentTaskConfirmation: function(task, componentId, callback) {
                    var modalWindow = $modal.open({
                        templateUrl: "/static/app/components/componentTaskDeleteTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.model = task;

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    componentService.deleteComponentTask({
                                        component_task_id: $innerScope.model.id
                                    }, function (data) {
                                        toaster.pop('success', "Success", "Task Deleted.");
                                        callback();
                                    }, function(httpResponse) {
                                        toaster.pop('error', "Failed", "Task Delete Failed.");
                                    }).$promise.finally(function(){
                                        modalWindow.close();
                                    });
                                };
                            }
                        ]
                    });
                }
            }
        }
    ])
    .factory("componentIssueManagementService", ["$modal", "componentService", "toaster",
        function($modal, componentService, toaster) {
            return {
                launchComponentIssueEditor: function(issue, componentId, issueData, callback) {
                    var mode = issue ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/components/componentIssueEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.forms = {};
                                $innerScope.mode = mode;
                                $innerScope.caption = mode == "edit" ? "Edit Issue" : "Add Issue";
                                $innerScope.viewModel = {
                                    priorities: issueData.priorities,
                                    statuses: issueData.statuses,
                                    types: issueData.types
                                };

                                $innerScope.model = issue ? angular.extend({}, issue) : {};

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    if ($innerScope.forms.issueForm.$valid) {
                                        if ($innerScope.model.id) {
                                            componentService.updateComponentIssue({
                                                component_id: componentId,
                                                component_issue_id: $innerScope.model.id
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Issue Updated.");
                                                callback();
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Issue Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        } else {
                                            $innerScope.model.component_id = componentId;

                                            componentService.insertComponentIssue({
                                                component_id: componentId
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Issue Created.");
                                                callback();
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Issue Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        }
                                    }
                                };
                            }
                        ]
                    });
                },
                launchDeleteComponentIssueConfirmation: function(issue, componentId, callback) {
                    var modalWindow = $modal.open({
                        templateUrl: "/static/app/components/componentIssueDeleteTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.model = issue;

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    componentService.deleteComponentIssue({
                                        component_issue_id: $innerScope.model.id
                                    }, function (data) {
                                        toaster.pop('success', "Success", "Issue Deleted.");
                                        callback();
                                    }, function(httpResponse) {
                                        toaster.pop('error', "Failed", "Delete Failed.");
                                    }).$promise.finally(function(){
                                        modalWindow.close();
                                    });
                                };
                            }
                        ]
                    });
                }
            }
        }
    ])
    .factory("equipmentTaskManagementService", ["$modal", "equipmentService", "toaster",
        function($modal, equipmentService, toaster) {
            return {
                launchComponentTaskEditor: function(task, equipmentId, taskData, callback) {
                    var mode = task ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/equipment/equipmentTaskEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.forms = {};
                                $innerScope.mode = mode;
                                $innerScope.caption = mode == "edit" ? "Edit Task" : "Add Task";
                                $innerScope.viewModel = {
                                    priorities: taskData.priorities,
                                    statuses: taskData.statuses,
                                    types: taskData.types
                                };

                                $innerScope.model = task ? angular.extend({}, task) : {};

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    if ($innerScope.forms.taskForm.$valid) {
                                        if ($innerScope.model.id) {
                                            equipmentService.updateEquipmentTask({
                                                equipment_task_id: $innerScope.model.id
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Task Updated.");
                                                callback($innerScope.model);
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Task Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        } else {
                                            $innerScope.model.equipment_id = equipmentId;

                                            equipmentService.insertEquipmentTask({
                                                equipment_id: equipmentId
                                            }, $innerScope.model, function (data) {
                                                var equipmentTask = $innerScope.model;
                                                equipmentTask.id = data.id;
                                                toaster.pop('success', "Success", "Task Created.");
                                                callback(equipmentTask);
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Task Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        }
                                    }
                                };
                            }
                        ]
                    });
                }
            }
        }
    ])
    .factory("equipmentIssueManagementService", ["$modal", "equipmentService", "toaster",
        function($modal, equipmentService, toaster) {
            return {
                launchComponentIssueEditor: function(issue, equipmentId, taskData, callback) {
                    var mode = issue ? "edit" : "create";
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/equipment/equipmentIssueEditorTemplate.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.forms = {};
                                $innerScope.mode = mode;
                                $innerScope.caption = mode == "edit" ? "Edit Issue" : "Add Issue";
                                $innerScope.viewModel = {
                                    priorities: taskData.priorities,
                                    statuses: taskData.statuses,
                                    types: taskData.types
                                };

                                $innerScope.model = issue ? angular.extend({}, issue) : {};

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    if ($innerScope.forms.issueForm.$valid) {
                                        if ($innerScope.model.id) {
                                            equipmentService.updateEquipmentIssue({
                                                equipment_issue_id: $innerScope.model.id
                                            }, $innerScope.model, function (data) {
                                                toaster.pop('success', "Success", "Issue Updated.");
                                                callback($innerScope.model);
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Issue Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        } else {
                                            $innerScope.model.equipment_id = equipmentId;

                                            equipmentService.insertEquipmentIssue({
                                                equipment_id: equipmentId
                                            }, $innerScope.model, function (data) {
                                                var equipmentIssue = $innerScope.model;
                                                equipmentIssue.id = data.id;
                                                toaster.pop('success', "Success", "Issue Created.");
                                                callback(equipmentIssue);
                                            }, function(httpResponse) {
                                                toaster.pop('error', "Failed", "Issue Save Failed.");
                                            }).$promise.finally(function(){
                                                modalWindow.close();
                                            });
                                        }
                                    }
                                };
                            }
                        ]
                    });
                }
            }
        }
    ])
    .factory("equipmentDashboardPointManagementService", ["$modal", "dataMappingService", "toaster",
        function($modal, dataMappingService, toaster) {
            return {
                launchPointUnmapConfirmation: function(point, callback) {
                    var modalWindow = $modal.open({
                        size: "lg",
                        templateUrl: "/static/app/equipment/equipmentUnmapPointModal.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.viewModel = {
                                    syrx_num: point.syrx_num
                                };

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    dataMappingService.unmapPoint({point_id:point.syrx_num}, function (data) {
                                        toaster.pop('success', "Success", "Point successfully unmapped.");
                                        callback();
                                    }, function(httpResponse) {
                                        toaster.pop('error', "Failed", "Failed to unmap point.");
                                    }).$promise.finally(function(){
                                        modalWindow.close();
                                    });
                                };
                            }
                        ]
                    });
                },
                launchGlobalPointConfirmation: function(point, callback) {
                    var modalWindow = $modal.open({
                        size: 'lg',
                        templateUrl: '/static/app/equipment/equipmentGlobalPointModal.html',
                        controller: ['$scope',
                            function($innerScope) {
                                $innerScope.viewModel = angular.copy(point);
                                $innerScope.viewModel.global = true;

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    callback($innerScope.viewModel);
                                    modalWindow.close();
                                };
                            }
                        ]
                    })
                }
            }
        }
    ])
    .factory("groupService", ["$resource",
        function($resource) {
            return $resource("/api/groups/:action/:id", // Define the base url, adding a parameter for the id
                { id: "@id" }, // Set up the parameters in the url -- in this case, map the id to the model's id, indicated by the @ sign
                { 'getAccounts': { method:"GET", isArray:true, params: { action:"GetAccounts" } } }
            );
        }
    ])
    .factory("componentService", ["$resource",
        function($resource) {
            return $resource("/api/components/:id", // Define the base url, adding a parameter for the id
                { id: "@id" }, // Set up the parameters in the url -- in this case, map the id to the model's id, indicated by the @ sign
                {
                    "removeMappingChild": {
                        method: "POST",
                        url: "/api/components/:id/removeMappingChild"
                    },
                    "removeMappingRoot": {
                        method: "POST",
                        url: "/api/components/removeMappingRoot"
                    },
                    "getPointsByComponentIds": {
                        method: "GET",
                        url: "/api/components/getPointsByComponentIds"
                    },
                    "addParagraph": {
                        method:"PUT",
                        url:"/api/components/paragraphs"
                    },
                    "getParagraph": {
                        method:"GET",
                        url:"/api/components/paragraphs/:id"
                    },
                    "deleteParagraph": {
                        method:"DELETE",
                        url:"/api/components/paragraphs/:id"
                    },
                    "getAllParagraphs": {
                        method: "GET",
                        url:"/api/components/getAllParagraphs"
                    },
                    "getComponentIssues": {
                        method:"GET",
                        url:"/api/components/:component_id/componentAndAncestorIssues"
                    },
                    "deleteComponentIssue": {
                        method:"DELETE",
                        url:"/api/components/issues/:component_issue_id"
                    },
                    "getComponentTasks": {
                        method:"GET",
                        url:"/api/components/:component_id/componentAndAncestorTasks"
                    },
                    "deleteComponentTask": {
                        method:"DELETE",
                        url:"/api/components/tasks/:component_task_id"
                    },
                    "getStructureChildren": {
                        method:"GET",
                        isArray:true,
                        url:"/api/components/getStructureChildrenOf?id=:id"
                    },
                    "getAvailableParagraphsByTypeAndCategory": {
                        method: "GET",
                        url:"/api/components/:component_id/:paragraph_type/:category_id"
                    },
                    "delete": {
                        method: "DELETE",
                        url: "/api/components/:id"
                    },
                    "update": {
                        method: "PUT",
                        url: "/api/components/"
                    }
                }
            );
        }
    ])

    .factory("weatherstationService", ["$resource",
        function($resource) {
            return $resource("/api/weatherstations/:id", // Define the base url, adding a parameter for the id
                { id: "@id" }, // Set up the parameters in the url -- in this case, map the id to the model's id, indicated by the @ sign
                {
                    "list": { method: "GET", url: "/api/weatherstations/list", isArray: true },
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("naicsService", ["$resource",
        function($resource) {
            return $resource("/api/Naics",
                {},
                {
                    "getLevelFive": { method: "GET", url: "/api/Naics/getLevelFive", isArray: true }
                }
            );
        }
    ])

    .factory("sicService", ["$resource",
        function($resource) {
            return $resource("/api/Sic",
                {},
                {
                    "getLevelTwo": { method: "GET", url: "/api/Sic/getLevelTwo", isArray: true }
                }
            );
        }
    ])

    .factory("accountService", ["$resource",
        function($resource) {
            return $resource("/api/accounts/:id", // Define the base url, adding a parameter for the id
                { id: "@id" }, // Set up the parameters in the url -- in this case, map the id to the model's id, indicated by the @ sign
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("timezoneService", ["$resource",
        function($resource) {
            return $resource("/api/timezones");
        }
    ])

    .factory("userService", [
        "$resource",
        function($resource) {
            return $resource("/api/Users/:id",
            { id: "@id" },
            {
                'update': { method: "PUT" },
                'notifications': { method: 'GET', url:'/api/Users/:id/Notifications', isArray: true},
                'deleteNotification': {method:'DELETE', url:'/api/Users/:id/Notifications/:notificationId'}
            });
        }
    ])

    .factory("roleService", [
        "$resource",
        function ($resource) {
            return $resource("/api/Roles/:action/:id",
                { id: "@id" },
                {
                    'GetInactive': { method: 'GET', isArray: true, params: { action: 'GetInactive' } },
                    'update': { method: 'PUT' },
                    'GetAll': { method: 'GET', isArray: true, params: { action: 'GetAll' } }
                }
            );
        }
    ])

    .factory("categoryService", [
        "$resource",
        function($resource) {
            return $resource("/api/Categories/:action/:id",
                { id: "@id" },
                {
                    'update':{method:"PUT"},
                    'GetAll':{method:"GET", isArray:true, params: { action: "GetAll" } }
                }
            );
        }
    ])

    .factory("syrxCategoryService", [
        "$resource",
        function($resource) {
            return $resource("/api/SyrxCategories/:action/:id",
                { id: "@id" },
                {
                    'update':{method:"PUT"},
                    'GetAll':{method:"GET", isArray:true, params: { action: "GetAll" } }
                }
            );
        }
    ])

    .factory("contactService", [
        "$resource",
        function($resource) {
            return $resource("/api/Contacts/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("taskService", [
        "$resource",
        function($resource) {
            return $resource("/api/Tasks/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAllAvailable': {
                        method: 'GET',
                        url:"/api/Tasks/:component_id/GetAllAvailable"
                    },
                    'GetAllAvailableEquipmentTasks': {
                        method: 'GET',
                        url:"/api/equipment/:equipment_id/GetAllAvailableTasks"
                    }
                }
            );
        }
    ])

    .factory("issueService", [
        "$resource",
        function($resource) {
            return $resource("/api/Issues/:id",
                {id:"@id"},
                {
                    'update':{ method:"PUT" },
                    'GetAllAvailable': {
                        method: 'GET',
                        url:"/api/Issues/:component_id/GetAllAvailable"
                    },
                    'GetAllAvailableEquipmentIssues': {
                        method: 'GET',
                        url:"/api/equipment/:equipment_id/GetAllAvailableIssues"
                    }
                }
            );
        }
    ])

    .factory("projectService", [
        "$resource",
        function($resource) {
            return $resource("/api/Projects/:action/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT"},
                    'GetAll':{method:"GET", isArray:true, params: { action: "GetAll" } }
                }
            );
        }
    ])

    .factory("ecoService", [
        "$resource",
        function($resource) {
            return $resource("/api/Eco/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("committeeService", [
        "$resource",
        function($resource) {
            return $resource("/api/Committees/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            )
        }
    ])

    .factory("meetingService", [
        "$resource",
        function($resource) {
            return $resource("/api/Meetings/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])


    .factory("meetingtypeService", [
        "$resource",
        function($resource) {
            return $resource("/api/MeetingTypes/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'getAll': { method: 'GET' }
                }
            );
        }
    ])

    .factory("utilitycompanyService", [
        "$resource",
        function($resource) {
            return $resource("/api/UtilityCompanies/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("taskPriorityService", [
        "$resource",
        function($resource) {
            return $resource("/api/TaskPriorities/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("taskStatusService", [
        "$resource",
        function($resource) {
            return $resource("/api/TaskStatuses/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("taskTypeService", [
        "$resource",
        function($resource) {
            return $resource("/api/TaskTypes/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("taskTableData", [
        "$q",
        "taskPriorityService",
        "taskStatusService",
        "taskTypeService",
        function($q, taskPriorityService, taskStatusService, taskTypeService) {
            return function() {
                var priorityPromise = taskPriorityService.GetAll().$promise;
                var statusPromise = taskStatusService.GetAll().$promise;
                var typePromise = taskTypeService.GetAll().$promise;

                return $q.all([priorityPromise, statusPromise, typePromise]).then(function(response) {
                    return {
                        priorities: response[0].data,
                        statuses: response[1].data,
                        types: response[2].data
                    };
                });
            };
        }
    ])

    .factory("issuePriorityService", [
        "$resource",
        function($resource) {
            return $resource("/api/IssuePriorities/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("issueStatusService", [
        "$resource",
        function($resource) {
            return $resource("/api/IssueStatuses/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("issueTypeService", [
        "$resource",
        function($resource) {
            return $resource("/api/IssueTypes/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" },
                    'GetAll': { method: "GET" }
                }
            );
        }
    ])

    .factory("issueTableData", [
        "$q",
        "issuePriorityService",
        "issueStatusService",
        "issueTypeService",
        function($q, issuePriorityService, issueStatusService, issueTypeService) {
            return function() {
                var priorityPromise = issuePriorityService.GetAll().$promise;
                var statusPromise = issueStatusService.GetAll().$promise;
                var typePromise = issueTypeService.GetAll().$promise;

                return $q.all([priorityPromise, statusPromise, typePromise]).then(function(response) {
                    return {
                        priorities: response[0].data,
                        statuses: response[1].data,
                        types: response[2].data
                    };
                });
            };
        }
    ])

    .factory("actionitempriorityService", [
        "$resource",
        function($resource) {
            return $resource("/api/ActionItemPriorities/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])
    .factory("actionitemstatusService", [
        "$resource",
        function($resource) {
            return $resource("/api/ActionItemStatuses/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("contractService", [
        "$resource",
        function($resource) {
            return $resource("/api/Contracts/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])

    .factory("actionitemtypeService", [
        "$resource",
        function($resource) {
            return $resource("/api/ActionItemTypes/:id",
                { id: "@id" },
                {
                    'update': { method: "PUT" }
                }
            );
        }
    ])
    .factory("reportingGroupService", [
        "$resource",
        function($resource) {
            return $resource("/api/ReportingGroups/:action/:id",
                { id: "@id" },
                {
                    'getIntensityData': {method:"POST", params: { action: "GetIntensityData" }},
                    'getTotalEnergyData': {method:"POST", isArray:true, params: {action:"GetTotalEnergyData"}},
                    'getBenchmarkPerformanceData': {method:'POST', params: { action: 'GetBenchmarkPerformanceData'}},
                    'getBenchmarkBudgetVarianceData': {method:'POST', isArray:true,  params: {action:'GetBenchmarkBudgetVarianceData'}},
                    'peakReport': {method:'POST', isArray:true, params: {action:'peak'}},
                    'GetEnergySummaryData': {method:'POST', params: { action: 'GetEnergySummaryData'}}
                }
            );
        }
    ])
    .factory("reportingNaicsService", [
        "$resource",
        function($resource) {
            return $resource("/api/ReportingNaics/:action/:id",
                { id: "@id" },
                {
                    'getIntensityData': {method:"POST", params: { action: "GetIntensityData" }},
                    'getTotalEnergyData': {method:"POST", isArray:true, params: {action:"GetTotalEnergyData"}},
                    'getGroups': {method: "GET", isArray:true, params: {action:"GetGroups"}},
                    'peakReport': {method:'POST', isArray:true, params: {action:'peak'}}
                }
            );
        }
    ])
    .factory("reportingSicService", [
        "$resource",
        function($resource) {
            return $resource("/api/ReportingSic/:action/:id",
                { id: "@id" },
                {
                    'getIntensityData': {method:"POST", params: { action: "GetIntensityData" }},
                    'getTotalEnergyData': {method:"POST", isArray:true, params: {action:"GetTotalEnergyData"}},
                    'getGroups': {method: "GET", isArray:true, params: {action:"GetGroups"}},
                    'peakReport': {method:'POST', isArray:true, params: {action:'peak'}}
                }
            );
        }
    ])
    .factory("reportingComponentService", [
        "$resource",
        function($resource) {
            return $resource("/api/ReportingComponents/:action/:id",
                { id: "@id" },
                {
                    'getIntensityData': {method:"POST", url:'/api/ReportingComponents/StandardsChart'},
                    'getStandardsTableData': {method:"POST", isArray:true, url:'/api/ReportingComponents/StandardsTable'},
                    'getComparisonData': {method:"POST", url:'/api/ReportingComponents/ComparisonChart'},
                    'getComparisonTableData': {method:"POST", url:'/api/ReportingComponents/ComparisonTable'},
                    'getDifferenceData': {method:"POST", url:'/api/ReportingComponents/DifferenceChart'},
                    'getEquipmentReport': {method:"POST", url:'/api/ReportingComponents/EquipmentReport'},
                    'getEquipmentReportTable': {method:'POST', url:'/api/ReportingComponents/EquipmentReportTable'}
                }
            );
        }
    ])
    .factory("textReportService", [
        "$resource",
        function($resource) {
            return $resource("/api/TextReports/:id",
                { id: "@id" },
                {
                    'getGroupReport': {method:"POST", url:"/api/TextReports/GroupsReport"},
                    'getNaicsReport': {method:'POST', url:'/api/TextReports/NaicsReport'},
                    'getSicReport': {method:'POST', url:'/api/TextReports/SicReport'}
                }
            );
        }
    ])
    .factory("uploadProgressService", [
        "$resource",
        function($resource) {
            return $resource("/api/energy_imports");
        }
    ])
    .factory("bronzeSubmissionService", [
        "$resource",
        function($resource) {
            return $resource("/api/BronzeReporting/:id",
                { id: "@id" },
                {
                    "process": {method: "POST"}
                }
            );
        }
    ])
    .factory("componentPointService", [
        "$resource",
        function($resource) {
            return $resource("",
                { },
                {
                    'getByComponent': { method: "GET", isArray: true, url: "/api/components/:component_id/pointList/:type"},
                    'insert': { method: "POST", url:"/api/components/:component_id/points" },
                    'update': { method: "PUT", url:"/api/components/:component_id/points/:point_id" },
                    'delete': { method: "DELETE", url:"/api/components/:component_id/points/:point_id" },
                    'parseFormula': { method: "POST", url:"/api/components/parseFormula" }
                }
            );
        }
    ])
    .factory("componentParagraphService", [
        "$resource",
        function($resource) {
            return $resource("",
                { },
                {
                    'getByComponent': { method: "GET", isArray: true, url: "/api/components/:component_id/paragraphList/:type"}
                }
            );
        }
    ])
    .factory("dataMappingService", [
        "$resource",
        function($resource) {
            return $resource("",
                { },
                {
                    'insertJohnson': { method: "POST", url: "/api/data_mapping/johnson"},
                    "removeJohnson": {method: "DELETE", url: "/api/data_mapping/johnson/:id"},
                    'insertFieldserver': { method: "POST", url: "/api/data_mapping/fieldserver"},
                    "removeFieldserver": {method: "DELETE", url: "/api/data_mapping/fieldserver/:id"},
                    'insertInvensys': {method: "POST", url: "/api/data_mapping/invensys"},
                    'removeInvensys': {method: "DELETE", url: "/api/data_mapping/invensys/:id"},
                    "insertSiemens": {method: "POST", url: "/api/data_mapping/siemens"},
                    "removeSiemens": {method: "DELETE", url: "/api/data_mapping/siemens/:id"},
                    'unmapPoint': {method: 'DELETE', url: '/api/data_mapping/:point_id'}
                }
            );
        }
    ])
    .factory("componentUploadService", [
        "$resource",
        function($resource) {
            return $resource("",
                {},
                {
                    "uploadComponents": {method:"POST", url:"/api/uploadComponents/:upload_id"},
                    "uploadComponentsProgress": {method:"GET", url:"/api/uploadComponents/:upload_id/progress"},
                    "uploadDryComponentsProgress": {method:"GET", url:"/api/uploadDryComponents/:upload_id/progress"},
                    "uploadDryComponentsResults": {method:"GET", url:"/api/uploadDryComponents/:upload_id/results"}
                });
        }
    ])
    .factory("userReportingGroupService", [
        "$resource",
        function($resource) {
            return $resource("",
                {},
                {
                    'updateReportingGroup': {method:"POST", url:'/api/Users/ReportingGroup'}
                }
            );
        }
    ])
    .factory("reportConfigurationSaveService", ["$modal", "savedReportConfigurationService",
        function($modal, savedReportConfigurationService) {
            return {
                launchConfigurationSaver: function(entities, configuration, reportType, callback) {
                    var modalWindow = $modal.open({
                        size: "sm",
                        templateUrl: "/static/app/saveReportConfiguration.html",
                        controller: ["$scope",
                            function($innerScope) {
                                $innerScope.report_type = reportType;
                                $innerScope.entity_ids = entities;
                                $innerScope.model = {
                                    'config_name': ""
                                };

                                $innerScope.cancel = function() {
                                    modalWindow.close();
                                };

                                $innerScope.submit = function() {
                                    var saveModel = {};

                                    saveModel.configuration = configuration;
                                    saveModel.entity_ids = $innerScope.entity_ids;
                                    saveModel.name = $innerScope.model.config_name;
                                    saveModel.report_type = $innerScope.report_type;
                                    savedReportConfigurationService.saveConfiguration(saveModel, function(response) {
                                        modalWindow.close();
                                        callback(response);
                                    });
                                };
                            }
                        ]
                    });
                }
            };
        }
    ])
    .factory("savedReportConfigurationService", [
        "$resource",
        function($resource) {
            return $resource("",
                {},
                {
                    'getSavedConfigurationsByType': {method: "GET", url: "/api/SavedReportConfigurations"},
                    'saveConfiguration': {method: "POST", url: '/api/SavedReportConfigurations'},
                    'getConfigurationById': {method:"GET", url:'/api/SavedReportConfigurations/:id'}
                }
            );
        }
    ]);