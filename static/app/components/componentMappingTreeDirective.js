angular.module("pathianApp.directives")
    .directive("componentMappingTree", ["$parse", "$timeout", "$compile", "componentTreeFactory",
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

                            if ("kendoDraggable" in attrs) {
                                $timeout(function() {
                                    var properties = $parse(attrs["kendoDraggable"])(scope)
                                    iElem.kendoDraggable({
                                        filter: "li.k-item .k-in",
                                        hint: function(e) {
                                            var item = $("<div class='k-header k-drag-clue'><span class='k-icon k-drag-status k-denied'></span>" + e.html() + "</div>");
                                            return item;
                                        },
                                        drag: properties.drag,
                                        dragstart: properties.dragstart,
                                        dragend: properties.dragend,
                                        cursorOffset: {
                                            left: 10,
                                            top: 10
                                        }
                                    });
                                }, 0, false);
                            }

                            var currentButtons = [];

                            scope.gridoptions.select = function(e) {

                                scope.selectedNode = undefined;
                                $(currentButtons).each(function() {
                                    this.remove();
                                })

                                var tree = iElem.data("kendoTreeView");
                                var dataItem = tree.dataItem(e.node);
                                var $node = $(e.node);
                                scope.selectedNode = $node;
                                scope.selectedDataItem = dataItem;
                                var $buttonTarget = $node.children("div");

                                var $deleteButton = $(document.createElement("button"))
                                    .attr("data-name", "component-mapping-tree-node-delete")
                                    .attr("ng-click", "delete(selectedNode, selectedDataItem)")
                                    .append("X");

                                currentButtons.push($deleteButton);
                                $buttonTarget.append($deleteButton);
                                $compile($deleteButton)(scope);
                            };

                            $compile($tree)(scope);
                        }
                    };
                }
            };
        }
    ]);