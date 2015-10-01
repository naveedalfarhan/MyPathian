angular.module("pathianApp.directives")
    .directive("reportingTree", ["$parse", "$timeout", "$compile",
        function ($parse, $timeout, $compile) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: true,
                compile: function (elem, attrs) {
                    // build the inner elements

                    var $tree = $(document.createElement("div"))
                        .attr("kendo-tree-view", "")
                        .attr("k-options", attrs["kOptions"])
                        .attr("kendo-drop-target", attrs["kendoDropTarget"])
                        .attr("selected-nodes", attrs["selectedNodes"])
                        .attr("forced-nodes", attrs["forcedNodes"])
                        .attr("service", attrs["treeType"]);

                    elem.replaceWith($tree);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile

                            scope.gridoptions = $parse(attrs["kOptions"])(scope);

                            $compile($tree)(scope);
                        }
                    };
                }
            };
        }
    ]);