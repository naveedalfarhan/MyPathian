angular.module("pathianApp.directives")
    .directive("componentIssueTable", ["$parse", "$compile",
        function ($parse, $compile) {
            return {
                templateUrl: "/static/app/components/componentIssueTable.html",
                scope: {
                    componentId: "="
                },
                compile: function(element, attributes) {
                    return function($scope, element, attributes) {
                        $scope.componentIssueGridOptions = {
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
                            toolbar: [{template:"<a class='k-button k-button-icontext k-grid-add' ng-click='addComponentIssue($event)'><span class='k-icon k-add'></span>Add Issue</a>"}],
                            columns: [
                                {
                                    field:"num",
                                    title:"Component #"
                                },
                                {field:"title", title:"Title"},
                                {
                                    command: [
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-edit' ng-click='editComponentIssue($event)'><span class='k-icon k-edit'></span>Edit</a>"
                                        },
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-delete' ng-click='deleteComponentIssue($event)'><span class='k-icon k-delete'></span>Delete</a>"
                                        }
                                    ]
                                }
                            ],
                            editable: false
                        };

                        var setComponentIssueGridOptions = function(component_id) {
                            $scope.componentIssueGridOptions.dataSource.transport.read.url = "/api/components/" + component_id + "/issues";
                        };

                        $scope.$watch("componentId", function() {
                            setComponentIssueGridOptions($scope.componentId);
                            var gridContainer = element.children("[grid-container]");
                            gridContainer.empty();
                            if ($scope.componentId) {
                                var grid = $("<div kendo-grid k-options='componentIssueGridOptions' k-data-source='componentIssueGridOptions.dataSource'></div>");
                                gridContainer.append(grid);
                                $compile(grid)($scope);
                            }
                        });
                    };
                },
                controller: ["$scope", "componentIssueManagementService", "issueTableData",
                    function($scope, componentIssueManagementService, issueTableData) {
                        $scope.addComponentIssue = function(event) {
                            issueTableData().then(function(issueTableData) {
                                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                                componentIssueManagementService.launchComponentIssueEditor(null, $scope.componentId, issueTableData,
                                    function() {
                                        grid.dataSource.read();
                                    });
                            });
                            return false;
                        };

                        $scope.editComponentIssue = function(event) {
                            var self = this;
                            issueTableData().then(function(issueTableData) {
                                var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                                componentIssueManagementService.launchComponentIssueEditor(self.dataItem, $scope.componentId, issueTableData,
                                    function() {
                                        grid.dataSource.read();
                                    });
                            });
                            return false;
                        };

                        $scope.deleteComponentIssue = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            componentIssueManagementService.launchDeleteComponentIssueConfirmation(this.dataItem, $scope.componentId,
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