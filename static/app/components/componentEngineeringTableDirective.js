angular.module("pathianApp.directives")
    .directive("componentEngineeringTable", ["$parse", "$compile",
        function ($parse, $compile) {
            return {
                templateUrl: "/static/app/components/componentEngineeringTable.html",
                scope: {
                    componentId: "="
                },
                compile: function(element, attributes) {
                    return function($scope, element, attributes) {
                        $scope.paragraphGridOptions = {
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
                                            type: { type: "string", validation: { required: true } }
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
                            toolbar: [{template:"<a class='k-button k-button-icontext k-grid-add' ng-click='addParagraph($event)'><span class='k-icon k-add'></span>Add paragraph</a>"}],
                            columns: [
                                {
                                    field:"type",
                                    title:"Type"
                                },
                                {
                                    field:"num",
                                    title:"Component Paragraph #"
                                },
                                {field:"title", title:"Title"},
                                {
                                    command: [
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-edit' ng-click='editParagraph($event)'><span class='k-icon k-edit'></span>Edit</a>"
                                        },
                                        {
                                            template: "<a class='k-button k-button-icontext k-grid-delete' ng-click='deleteParagraph($event)'><span class='k-icon k-delete'></span>Delete</a>"
                                        }
                                    ]
                                }
                            ],
                            editable: false
                        };

                        var setParagraphGridOptions = function(component_id) {
                            $scope.paragraphGridOptions.dataSource.transport.read.url = "/api/components/" + component_id + "/paragraphs";
                        };

                        $scope.$watch("componentId", function() {
                            setParagraphGridOptions($scope.componentId);
                            var gridContainer = element.children("[grid-container]");
                            gridContainer.empty();
                            if ($scope.componentId) {
                                var grid = $("<div kendo-grid k-on-change='paragraphGridSelect(kendoEvent)' k-options='paragraphGridOptions' k-data-source='paragraphGridOptions.dataSource'></div>");
                                gridContainer.append(grid);
                                $compile(grid)($scope);
                            }
                        });
                    };
                },
                controller: ["$scope", "paragraphManagementService",
                    function($scope, paragraphManagementService) {
                        $scope.selectedParagraphHtml = null;

                        $scope.addParagraph = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            paragraphManagementService.launchParagraphEditor(null, $scope.componentId,
                                function() {
                                    $scope.selectedParagraphHtml = null;
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.editParagraph = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            paragraphManagementService.launchParagraphEditor(this.dataItem, $scope.componentId,
                                function() {
                                    $scope.selectedParagraphHtml = null;
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.deleteParagraph = function(event) {
                            var grid = $(event.target).closest(".k-grid").data("kendoGrid");
                            paragraphManagementService.launchDeleteParagraphConfirmation(this.dataItem, $scope.componentId,
                                function() {
                                    $scope.selectedParagraphHtml = null;
                                    grid.dataSource.read();
                                });
                            return false;
                        };

                        $scope.paragraphGridSelect = function(e) {
                            var selectedRow = e.sender.dataItem(e.sender.select());
                            $scope.selectedParagraphHtml = selectedRow ? selectedRow.description : null
                        };
                    }
                ]
            }
        }
    ]);