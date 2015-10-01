angular.module('pathianApp.directives')
    .directive('dashboardTable', function($compile) {
        return {
            // High priority to execute right after the chart
            priority: 14999,
            // Terminal prevents any other directive from compiling on first pass
            terminal: true,
            compile: function(elem, attrs) {
                // Create the benchmark performance table
                var $benchmarkPerformanceTable = $(document.createElement('div'))
                    .attr('benchmark-performance-table', attrs.dashboardTable);
                var $benchmarkPerformanceWrapper = $(document.createElement('div'))
                    .attr('class', 'row');
                $benchmarkPerformanceWrapper.append($benchmarkPerformanceTable);
                elem.append($benchmarkPerformanceWrapper);

                // Create the benchmark budget variance table
                var $benchmarkBudgetVarianceTable = $(document.createElement('div'))
                    .attr('benchmark-budget-variance-table', attrs.dashboardTable);
                var $benchmarkBudgetVarianceWrapper = $(document.createElement('div'))
                    .attr('class', 'row');
                $benchmarkBudgetVarianceWrapper.append('<h4>Budget Variances</h4>');
                $benchmarkBudgetVarianceWrapper.append($benchmarkBudgetVarianceTable);
                elem.append($benchmarkBudgetVarianceWrapper);
                return function(scope, iElem) {
                    // When linking just delegate the link function returned by the new compile

                    var compiler = function() {
                        $compile(iElem.find("[benchmark-performance-table]"))(scope);
                        $compile(iElem.find("[benchmark-budget-variance-table]"))(scope);
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