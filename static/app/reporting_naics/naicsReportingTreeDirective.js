angular.module("pathianApp.directives")
    .directive("naicsReportingTree", ["$parse", "$timeout", "$compile", "reportingNaicsService",
        function($parse, $timeout, $compile, reportingNaicsService) {
            return {
                compile: function(elem, attrs) {

                    var $tree = $(document.createElement("div"))
                        .attr("selectable-tree-view", "")
                        .attr("selection-style", "multiple")
                        .attr("k-options", "gridoptions")
                        .attr("ng-bind", attrs["ngBind"])
                        .attr("ng-model", attrs["ngModel"]);

                    elem.replaceWith($tree);

                    return {
                        post: function(scope) {
                            scope.gridoptions = $parse(attrs["kOptions"])(scope);
                            $compile($tree)(scope);
                        }
                    };
                }
            }
        }
    ]);