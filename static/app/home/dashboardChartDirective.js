angular.module('pathianApp.directives')
    .directive('dashboardChart', function($compile) {
        return {
            // High priority to execute first
            priority: 15000,
            // Terminal prevents any other directive from compiling on first pass
            terminal: true,
            compile: function(elem, attrs) {
                // Create the chart
                var $reportingConsumptionChart = $(document.createElement('div'))
                    .attr('reporting-consumption-chart', 'model');
                elem.append($reportingConsumptionChart);
                return function(scope, iElem) {
                    // When linking just delegate the link function returned by the new compile

                    var compiler = function() {
                        $compile(iElem.children("[reporting-consumption-chart]"))(scope);
                    };
                    // Add a watch to model subproperties
                    scope.$watch('model.account_type', function(newValue, oldValue) {
                        if (newValue === oldValue)
                            return;
                        compiler();
                    });

                    scope.$watch('model.group_ids', function(newValue, oldValue) {
                        if (newValue === oldValue)
                            return;
                        compiler();
                    });

                    scope.$watch('model.benchmark_year', function(newValue, oldValue) {
                        if (newValue === oldValue)
                            return;
                        compiler();
                    });

                    if (scope.model)
                        compiler();
                }
            }
        }
    });