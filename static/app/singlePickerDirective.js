angular.module("pathianApp.directives")
    .directive("singlePicker", ["$parse", "$timeout", "$compile",
        function ($parse, $timeout, $compile) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                compile: function (elem, attrs) {
                    // build the inner elements

                    var $ul = $(document.createElement("ul"))
                        .attr("multipicker-list", "")
                        .append($(document.createElement("li"))
                            .attr("ng-hide", attrs["singlePicker"] + " === null")
                            .attr("ng-bind", attrs["singlePicker"] + "." + attrs["singlePickerCaptionProp"]));

                    var $kendoGridDiv = $(document.createElement("div"))
                        .attr("kendo-grid", "")
                        .attr("kendo-singlepicker", attrs["singlePicker"])
                        .attr("kendo-singlepicker-key-prop", attrs["singlePickerKeyProp"])
                        .attr("kendo-singlepicker-caption-prop", attrs["singlePickerCaptionProp"])
                        .attr("k-options", attrs["singlePickerOptions"] + ".options")
                        .attr("k-data-source", attrs["singlePickerOptions"] + ".dataSource")
                        .attr("k-selectable", "'single'");

                    elem.append($ul).append($kendoGridDiv);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile
                            $compile(iElem.children("ul"))(scope);
                            $compile(iElem.children("div"))(scope);
                        }
                    };
                }
            };
        }
    ])
    .directive("kendoSinglepicker", ["$parse", "$timeout",
        function ($parse, $timeout) {
            return {
                link: function (scope, elem, attrs) {
                    var scopePropGetter = $parse(attrs["kendoSinglepicker"]);
                    var keyProp = attrs["kendoSinglepickerKeyProp"];
                    var captionProp = attrs["kendoSinglepickerCaptionProp"];

                    $timeout(function () {
                        var grid = elem.data("kendoGrid");




                        var updateGridFromScope = function (scopePropSelected) {
                            $(grid._data).each(function () {
                                var $tr = grid.table.find("tr[data-uid='" + this.uid + "']");
                                var checkRow = scopePropSelected !== null && scopePropSelected !== undefined && scopePropSelected[keyProp] == this[keyProp];

                                if ($tr.length > 0 && checkRow && !$tr.hasClass("k-state-selected")) {
                                    // if it's in the scope property but not selected on the grid, select it on the grid
                                    $tr.addClass("k-state-selected");
                                } else if ($tr.length > 0 && !checkRow && $tr.hasClass("k-state-selected")) {
                                    // if it's not in the scope property but selected on the grid, unselect it on the grid
                                    $tr.removeClass("k-state-selected");
                                }
                            });
                        };

                        var updateScopeFromGrid = function () {
                            var selectedTr = grid.select();
                            if (selectedTr.length == 0) {
                                scopePropGetter.assign(scope, null);
                            } else {
                                var dataItem = grid.dataItem(selectedTr);
                                var o = {};
                                o[keyProp] = dataItem[keyProp];
                                o[captionProp] = dataItem[captionProp];
                                scopePropGetter.assign(scope, o);
                            }

                            scope.$apply();
                        };



                        var events = grid._events;

                        if (events.change === undefined)
                            events.change = [];
                        events.change.push(updateScopeFromGrid);

                        if (events.dataBound === undefined)
                            events.dataBound = [];
                        events.dataBound.push(function () {
                            var selectedKeys = scopePropGetter(scope);
                            updateGridFromScope(selectedKeys);
                        });

                        scope.$watchCollection(attrs["kendoMultipicker"], updateGridFromScope);
                    }, 50, false);

                }
            };
        }
    ])