angular.module("pathianApp.directives")
    .directive("componentPointTree", ["$parse", "$timeout", "$compile", "componentTreeFactory",
        function ($parse, $timeout, $compile, componentTreeFactory) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: true,
                compile: function (elem, attrs) {
                    // build the inner elements

                    var $tree = $(document.createElement("div"))
                        .attr("kendo-tree-view", "")
                        .attr("k-options", "gridoptions");

                    if ("edit" in attrs)
                        $tree.attr("edit", attrs["edit"]);

                    elem.replaceWith($tree)

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile

                            scope.gridoptions = $parse(attrs["kOptions"])(scope);
							
							var selectedNodeSetter = $parse(attrs["componentPointTree"]).assign;


                            scope.gridoptions.change = function(e) {

								
                                var tree = iElem.data("kendoTreeView");
                                var dataItem = tree.dataItem(tree.select());
								selectedNodeSetter(scope.$parent, dataItem);
								scope.$parent.$apply();
								
                            };

                            $compile($tree)(scope);
                        }
                    };
                }
            };
        }
    ]);