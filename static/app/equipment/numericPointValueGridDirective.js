angular.module("pathianApp.directives")
    .directive("numericPointValuesGrid", ["$parse", "$timeout", "$compile", "$rootScope",
        function($parse, $timeout, $compile, $rootScope) {

            return {
                priority: 900, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: {
                    equipmentPointId: "="
                },
                link: function (scope, iElem, attrs) {
                    scope.$watch("equipmentPointId", function() {
                        scope.gridOptions = {
                            dataSource: {
                                transport: {
                                    read: {
                                        url: "/api/equipment/numeric_points/" + scope.equipmentPointId + "/values",
                                        dataType: "json",
                                        contentType: "application/json",
                                        type: "GET"
                                    },
                                    update: {
                                        url: function (options) {
                                            return "/api/equipment/numeric_points/" + scope.equipmentPointId + "/values/" + options.id;
                                        },
                                        dataType: "json",
                                        contentType: "application/json",
                                        type: "PUT"
                                    },
                                    destroy: {
                                        url: function (options) {
                                            return "/api/equipment/numeric_points/" + scope.equipmentPointId + "/values/" + options.id;
                                        },
                                        dataType: "json",
                                        contentType: "application/json",
                                        type: "DELETE"
                                    },
                                    create: {
                                        url: "/api/equipment/numeric_points/" + scope.equipmentPointId + "/values",
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
                                    model: {
                                        id: "id",
                                        fields: {
                                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                                            effective_date: { type: "date", validation: { required: true } },
                                            value: { type: "number", validation: { required: true } },
                                            note: { type: "string", validation: {required: false } }
                                        }
                                    }
                                },
                                pageSize: 10,
                                serverPaging: false,
                                serverFiltering: false,
                                serverSorting: false
                            },
                            scrollable: false,
                            filterable: true,
                            sortable: { mode: "multiple" },
                            pageable: true,
                            toolbar: ["create"],
                            columns: [
                                {field: "effective_date", title: "Effective Date", template: "#= kendo.toString(effective_date, 'MM/dd/yyyy') #"},
                                {field: "value", title: "Value"},
                                {field: "note", title: "Note"},
                                {
                                    command: ["edit", "destroy"], title: "&nbsp;", width: "172px"
                                }
                            ],
                            editable: "inline"
                        };

                        var $grid = $("<div kendo-grid k-options='gridOptions'></div>");
                        iElem.empty().append($grid);
                        $compile(iElem.children("div"))(scope);
                    });
                }
            }
        }
    ]);