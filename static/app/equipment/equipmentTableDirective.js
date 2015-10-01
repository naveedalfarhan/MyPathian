angular.module("pathianApp.directives")
    .directive("equipmentTable", ["$parse", "$compile", "$location", "$rootScope",
        function($parse, $compile, $location, $rootScope) {
            return {
                template: "<h3>Group: {{selectedGroup.name}}</h3><div grid-container></div>",
                link: function($scope, element, attributes) {

                    var gridEditButton_click = function(e) {
                        var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                        $location.path("/commissioning/equipment/" + id + "/edit");
                        $scope.$apply();
                    };

                    var gridDeleteButton_click = function(e) {
                        var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                        $location.path("/commissioning/equipment/" + id + "/delete");
                        $scope.$apply();
                    };

                    var gridParagraphsButton_click = function(e) {
                        var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                        $location.path("/commissioning/equipment/" + id + "/paragraphs");
                        $scope.$apply();
                    };

                    var gridMappingsButton_click = function(e) {
                        var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                        $location.path("/commissioning/equipment/" + id + "/mappings");
                        $scope.$apply();
                    };

                    var setGridOptions = function(group_id) {
                        $scope.equipmentGridOptions = $rootScope.global.getJsonGridOptions({
                            controllerName: "equipmentForGroup/" + group_id,
                            model: {
                                id: "id",
                                fields: {
                                    id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                                    num: { type: "string" },
                                    name: { type: "string", validation: { required: true } }
                                }
                            },
                            columns: ["num", "name",
                                {
                                    template: "<a style='min-width: 0' class='k-button k-button-icontext k-grid-edit' href='\\#/commissioning/equipment/#=id#/edit'><span class='k-icon k-edit'></span>Edit</a>" +
                                              "<a style='min-width: 0' class='k-button k-button-icontext k-grid-delete' href='\\#/commissioning/equipment/#=id#/delete'><span class='k-icon k-delete'></span>Delete</a>" +
                                              "<a class='k-button k-button-icontext k-grid-paragraphs' href='\\#/commissioning/equipment/#=id#/dashboard'><span class='k-icon k-justifyLeft'></span>Dashboard</a>",
                                    filterable: false,
                                    sortable: false
                                }
                            ],
                            editable: false,
                            createTemplate: "<a class='k-button k-button-icontext k-grid-add' href='\\#/commissioning/equipment/new/" + group_id + "'><span class='k-icon k-add'></span>Add new record</a>",
                            defaultSort: { field: "Name", dir: "asc" }
                        });
                    };

                    $scope.$watch("selectedGroup.id", function() {
                        var gridContainer = element.find("[grid-container]");
                        gridContainer.empty();
                        if (!$scope.selectedGroup)
                            return;
                        setGridOptions($scope.selectedGroup.id);
                        var grid = $("<div kendo-grid k-options='equipmentGridOptions.options' k-data-source='equipmentGridOptions.dataSource'></div>");
                        gridContainer.append(grid);
                        $compile(grid)($scope);
                    });
                }
            }
        }
    ]);
