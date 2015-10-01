angular.module("pathianApp.directives")
    .directive("componentReportingTree", ["$parse", "$timeout", "$compile", "componentTreeFactory",
        function ($parse, $timeout, $compile, componentTreeFactory) {
            return {
                compile: function(elem, attrs) {
                    var $tree = $(document.createElement("div"))
                        .attr("selectable-tree-view", "")
                        .attr("selection-style", "multiple")
                        .attr("k-options", "options")
                        .attr("ng-bind", attrs["ngBind"])
                        .attr("ng-model", attrs["ngModel"]);

                    elem.replaceWith($tree);

                    return {
                        post: function(scope) {
                            scope.options = $parse(attrs['options'])(scope);
                            $compile($tree)(scope);
                        }
                    };
                }
            }
        }
    ]);