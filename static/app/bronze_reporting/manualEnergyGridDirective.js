angular.module("pathianApp.directives")
    .directive("manualEnergyGrid", ["$parse", "$timeout", "$compile",
        function ($parse, $timeout, $compile) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: true,
                compile: function (elem, attrs) {
                    var $kendoGridDiv = $(document.createElement("div"))
                        .attr("kendo-grid", "")
                        .attr("k-options", "gridOptions");

                    elem.replaceWith($kendoGridDiv);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            var data = [];
                            var model = undefined;
                            if ("ngModel" in iAttrs) {
                                model = $parse(iAttrs["ngModel"])(scope);
                                data = model;
                            }

                            var grid_change = function() {
                                if (!model)
                                    return;
                                var gridData = iElem.data("kendoGrid").dataSource.data();
                                console.log(gridData)

                                // convert model to dictionary keyed by uid
                                modelDict = {};
                                for (var x = 0; x < model.length; ++x)
                                    modelDict[model[x]["uid"]] = model[x];

                                // convert grid to dictionary keyed by uid
                                gridDataDict = {};
                                for (var x = 0; x < gridData.length; ++x)
                                    gridDataDict[gridData[x]["uid"]] = gridData[x];

                                // if model contains elements that AREN'T present in
                                // gridData, delete them
                                for (var x = model.length - 1; x >= 0; --x) {
                                    if (!gridDataDict[model[x]["uid"]])
                                        model.splice(x, 1);
                                }

                                // loop through gridData items, if item IS present in
                                // model, update it, otherwise add it
                                for (var x = 0; x < gridData.length; ++x) {
                                    var modelItem = modelDict[gridData[x]["uid"]];
                                    if (modelItem) {
                                        for (var fieldName in gridData[x].fields) {
                                            modelItem[fieldName] = gridData[x][fieldName];
                                        }
                                    } else {
                                        modelItem = {
                                            uid: gridData[x]["uid"]
                                        };
                                        for (var fieldName in gridData[x].fields) {
                                            modelItem[fieldName] = gridData[x][fieldName];
                                        }
                                        model.push(modelItem);
                                    }
                                }

                                scope.$apply();
                            };

                            scope.gridOptions = {
                                dataSource: {
                                    data: data,
                                    schema: {
                                        model: {
                                            fields: {
                                                StartDate: {type: "date", validation: {required: true}},
                                                EndDate: {type: "date", validation: {required: true}},
                                                Usage: {type: "number", validation: {required: true}},
                                                Cost: {type: "number", validation: {required: true}}
                                            }
                                        }
                                    },
                                    change: grid_change
                                },
                                navigatable: true,
                                pageable: true,
                                height: 400,
                                toolbar: ["create"],
                                columns: [
                                    { field: "StartDate", title: "Start Date", template: "#= kendo.toString(StartDate, 'd') #" },
                                    { field: "EndDate", title: "End Date", template: "#= kendo.toString(EndDate, 'd') #" },
                                    { field: "Usage", title: "Energy Usage" },
                                    { field: "Cost", title: "Cost" },
                                    { command: "destroy", title: "&nbsp;" }],
                                editable: {
                                    createAt: "bottom"
                                }
                            };
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile
                            $compile(iElem)(scope);
                        }
                    };
                }
            };
        }
    ]);