angular.module("pathianApp.directives")
    .directive("componentTaskTable", ["$parse", "$compile",
        function ($parse, $compile) {
            return {
                templateUrl: "/static/app/components/componentTaskTable.html",
                scope: {
                    componentId: "="
                },
                compile: function(element, attributes) {
                    return function($scope, element, attributes) {
                        $scope.componentTaskGridOptions = {
                            dataSource: {
                                transport: {
                                    read: {url: null, dataType: "json", contentType: "application/json", type: "GET"},
                                    update: {url: null, dataType: "json", contentType: "application/json", type: "PUT"},
                                    destroy: {url: null, dataType: "json", contentType: "application/json", type: "DELETE"},
                                    create: {url: null, dataType: "json", contentType: "application/json", type: "POST"},
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
                                    data: "data",
                                    total: "total",
                                    model: {
                                        id: "id",
                                        fields: {
                                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                                            num: { type: "string", validation: { required: false } },
                                            title: { type: "string", validation: { required: true } },
                                            description: { type: "string", validation: { required: true } },
                                            type: { type: "string", validation: { required: true } },
                                            status: { type: "string", validation: { required: true } },
                                            priority: { type: "string", validation: { required: true } }
                                        }
                                    }
                                },
                                pageSize: 10,
                                serverPaging: true
                            },
                            scrollable: false,
                            filterable: false,
                            sortable: false,
                            pageable: true,
                            selectable:"single",
                            toolbar: [{template:"<a class='k-button k-button-icontext k-grid-add' ng-click='addComponentTask($event)'><span class='k-icon k-add'></span>Add Task</a>"}],
                            columns: [
                                {
                                    field:"num",
                                    title:"Component #"
                                },
                                {field:"title", title:"Title"},
                                {
                                    command: [
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-edit' ng-click='editComponentTask($event)'><span class='k-icon k-edit'></span>Edit</a>"
                                        },
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-delete' ng-click='deleteComponentTask($event)'><span class='k-icon k-delete'></span>Delete</a>"
                                        }
                                    ]
                                }
                            ],
                            editable: false
                        };

                        var setComponentTaskGridOptions = function(component_id) {
                            $scope.componentTaskGridOptions.dataSource.transport.read.url = "/api/components/" + component_id + "/tasks";
                        };

                        $scope.$watch("componentId", function() {
                            setComponentTaskGridOptions($scope.componentId);
                            var gridContainer = element.children("[grid-container]");
                            gridContainer.empty();
                            if ($scope.componentId) {
                                var grid = $("<div kendo-grid k-options='componentTaskGridOptions' k-data-source='componentTaskGridOptions.dataSource'></div>");
                                gridContainer.append(grid);
                                $compile(grid)($scope);
                            }
                        });
                    };
                },
                controller: ["$scope", "componentTaskManagementService", "taskTableData",
                    function($scope, componentTaskManagementService, taskTableData) {
                        $scope.addComponentTask = function(event) {
                            taskTableData().then(function(taskTableData) {
                                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                                componentTaskManagementService.launchComponentTaskEditor(null, $scope.componentId, taskTableData, function() {
                                    grid.dataSource.read();
                                });
                            });
                            
                            return false;
                        };

                        $scope.editComponentTask = function(event) {
                            var self = this;
                            taskTableData().then(function(taskTableData) {
                                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                                componentTaskManagementService.launchComponentTaskEditor(self.dataItem, $scope.componentId, taskTableData, function() {
                                        grid.dataSource.read();
                                });
                            });
                            return false;
                        };

                        $scope.deleteComponentTask = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            componentTaskManagementService.launchDeleteComponentTaskConfirmation(this.dataItem, $scope.componentId,
                                function() {
                                    grid.dataSource.read();
                                });
                            return false;
                        };
                    }
                ]
            }
        }
    ]);