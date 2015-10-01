angular.module("pathianApp.directives")
    .directive("groupTree", ["$parse", "$timeout", "$compile", "groupTreeFactory",
        function ($parse, $timeout, $compile, groupTreeFactory) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: true,
                compile: function (elem, attrs) {
                    // build the inner elements

                    var $tree = $(document.createElement("div"))
                        .attr("selectable-tree-view", "")
                        .attr("selection-style", attrs["selectionStyle"])
                        .attr("k-options", "gridoptions")
                        .attr("kendo-drop-target", attrs["kendoDropTarget"])
                        .attr("ng-bind", attrs["ngBind"])
                        .attr("ng-model", attrs["ngModel"]);

                    elem.append($tree);



                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile

                            scope.gridoptions = $parse(attrs["kOptions"])(scope);

                            scope.gridoptions.select = function(e) {

                                scope.selectedNode = undefined;

                                var $node = $(e.node);
                                var $innerSpan = $node.find(".k-in");
                                var innerSpanWidth = $innerSpan.width();
                                var innerSpanOffset = $innerSpan.offset();

                                $("[data-name='group-tree-node-delete']").remove();


                                var $parentNode = $node.parent().closest(".k-item");
                                if ("groupTreeRemove" in iAttrs) {
                                    scope.selectedNode = $node;
                                    var $buttonTarget = $node.children("div");
                                    var $button = $(document.createElement("button"))
                                        .attr("data-name", "group-tree-node-delete")
                                        .attr("ng-click", "remove()")
                                        .append("X");
                                    $buttonTarget.append($button);

                                    $compile($button)(scope);
                                }
                            };

                            scope.remove = function() {
                                groupTreeFactory.removeChild(scope.selectedNode);
                            };

                            $compile(iElem.children("[selectable-tree-view]"))(scope);
                        }
                    };
                }
            };
        }
    ]);