angular.module("pathianApp.directives")
    .directive("componentPointTable", ["$parse", "$compile",
        function ($parse, $compile) {
            return {
                templateUrl: "/static/app/components/componentPointTable.html",
                scope: {
                    componentId: "="
                },
                compile: function(element, attributes) {
                    return function($scope, element, attributes) {
                        $scope.pointGridOptions = {
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
                                            component_point_num: { type: "string", validation: { required: false } },
                                            description: { type: "string", validation: { required: true } },
                                            point_type: { type: "string", validation: { required: true } },
                                            point_type_caption: { type: "string" },
                                            code: { type: "string" },
                                            units: { type: "string" },
                                            formula: { type: "string" },
                                            master_point: { type: "boolean" }
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
                            toolbar: [{template:"<a class='k-button k-button-icontext k-grid-add' ng-click='addPoint($event)'><span class='k-icon k-add'></span>Add point</a>"}],
                            columns: [
                                {
                                    field:"point_type",
                                    title:"Type"
                                },
                                {
                                    field:"component_point_num",
                                    title:"Component Point #"
                                },
                                {field:"code", title:"Code"},
                                {field:"description", title:"Description"},
                                {field:"units", title:"Units"},
                                {
                                    template: "# if (!master_point) {# <a class='k-button k-button-icontext k-grid-edit' ng-click='setMasterPoint($event)'><span class='k-icon k-i-tick'></span>Set As Master Point</a> #} else {# <span>Current Master Point</span> #}#"
                                },
                                {
                                    command: [
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-edit' ng-click='editPoint($event)'><span class='k-icon k-edit'></span>Edit</a>"
                                        },
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-delete' ng-click='deletePoint($event)'><span class='k-icon k-delete'></span>Delete</a>"
                                        }
                                    ]
                                }
                            ],
                            editable: false
                        };

                        var setPointGridOptions = function(component_id) {
                            $scope.pointGridOptions.dataSource.transport.read.url = "/api/components/" + component_id + "/points";
                            $scope.pointGridOptions.dataSource.transport.create.url = "/api/components/" + component_id + "/points";
                            $scope.pointGridOptions.dataSource.transport.update.url =
                                function (options) {
                                    return "/api/components/" + component_id + "/points/" + options.id;
                                };
                            $scope.pointGridOptions.dataSource.transport.destroy.url =
                                function (options) {
                                    return "/api/components/" + component_id + "/points/" + options.id;
                                };
                        };

                        $scope.$watch("componentId", function() {
                            setPointGridOptions($scope.componentId);
                            var gridContainer = element.children("[grid-container]");
                            gridContainer.empty();
                            var grid = $("<div kendo-grid k-options='pointGridOptions' k-data-source='pointGridOptions.dataSource'></div>");
                            gridContainer.append(grid);
                            $compile(grid)($scope);
                        });
                    };
                },
                controller: ["$scope", "pointManagementService",
                    function($scope, pointManagementService) {
                        $scope.addPoint = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            pointManagementService.launchPointEditor(null, $scope.componentId,
                                function() {
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.editPoint = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            pointManagementService.launchPointEditor(this.dataItem, $scope.componentId,
                                function() {
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.deletePoint = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            pointManagementService.launchDeletePointConfirmation(this.dataItem, $scope.componentId,
                                function() {
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.setMasterPoint = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            pointManagementService.setMasterPoint(this.dataItem, $scope.componentId,
                                function () {
                                    grid.dataSource.read();
                                });
                            return false;
                        }
                    }
                ]
            }
        }
    ]);