angular.module("pathianApp.directives")
    .directive("multiPicker", ["$parse", "$timeout", "$compile",
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
                            .attr("ng-repeat", "e in " + attrs["multiPicker"])
                            .attr("ng-bind", "e." + attrs["multiPickerCaptionProp"]));

                    var $kendoGridDiv = $(document.createElement("div"))
                        .attr("kendo-grid", "")
                        .attr("kendo-multipicker", attrs["multiPicker"])
                        .attr("kendo-multipicker-key-prop", attrs["multiPickerKeyProp"])
                        .attr("kendo-multipicker-caption-prop", attrs["multiPickerCaptionProp"])
                        .attr("k-options", attrs.multiPickerOptions + ".options")
                        .attr("k-data-source", attrs.multiPickerOptions + ".dataSource")
                        .attr("k-selectable", "'multiple'");

                    elem.append($ul).append($kendoGridDiv);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile
                            $compile($ul)(scope);
                            $compile($kendoGridDiv)(scope);
                        }
                    };
                }
            };
        }
    ])
    .directive("kendoMultipicker", ["$parse", "$timeout",
        function ($parse, $timeout) {
            return {
                link: function (scope, elem, attrs) {
                    var scopePropGetter = $parse(attrs["kendoMultipicker"]);
                    var keyProp = attrs["kendoMultipickerKeyProp"];
                    var captionProp = attrs["kendoMultipickerCaptionProp"];

                    $timeout(function () {
                        var grid = elem.data("kendoGrid");




                        var updateGridFromScope = function (scopePropSelected) {
                            var dict = {};
                            if (scopePropSelected === undefined || scopePropSelected === null)
                                return;

                            for (var i = 0; i < scopePropSelected.length; ++i) {
                                var key = scopePropSelected[i][keyProp];
                                var caption = scopePropSelected[i][captionProp];
                                dict[key] = {
                                    key: key,
                                    caption: caption
                                };
                            }
                            $(grid._data).each(function () {
                                var $tr = grid.table.find("tr[data-uid='" + this.uid + "']");
                                var scopePropHasKey = dict.hasOwnProperty(this[keyProp]);

                                if ($tr.length > 0 && scopePropHasKey && !$tr.hasClass("k-state-selected")) {
                                    // if it's in the scope property but not selected on the grid, select it on the grid
                                    $tr.addClass("k-state-selected");
                                } else if ($tr.length > 0 && !scopePropHasKey && $tr.hasClass("k-state-selected")) {
                                    // if it's not in the scope property but selected on the grid, unselect it on the grid
                                    $tr.removeClass("k-state-selected");
                                }
                            });
                        };

                        var updateScopeFromGrid = function () {
                            var scopePropSelected = scopePropGetter(scope);
                            var dict = {};


                            if (scopePropSelected === undefined || scopePropSelected === null)
                                return;

                            for (var i = 0; i < scopePropSelected.length; ++i) {
                                var item = scopePropSelected[i];
                                dict[item[keyProp]] = {
                                    key: item[keyProp],
                                    caption: item[captionProp]
                                }
                            }

                            $(grid._data).each(function () {
                                var $tr = grid.table.find("tr[data-uid='" + this.uid + "']");
                                if (!$tr.length)
                                    return;

                                var scopePropHasKey = dict.hasOwnProperty(this[keyProp]);
                                var selectedOnGrid = $tr.hasClass("k-state-selected");

                                if (scopePropHasKey && !selectedOnGrid) {
                                    // if it's in the scope property but not selected on the grid, remove it from the scope property
                                    delete dict[this[keyProp]];
                                } else if (!scopePropHasKey && selectedOnGrid) {
                                    // if it's not in the scope property but selected on the grid, add it to the scope property
                                    dict[this[keyProp]] = {
                                        key: this[keyProp],
                                        caption: this[captionProp]
                                    };
                                }
                            });

                            scopePropSelected.length = 0;
                            for (var k in dict) {
                                var o = {};
                                o[keyProp] = dict[k].key;
                                o[captionProp] = dict[k].caption;
                                scopePropSelected.push(o);
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