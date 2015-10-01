angular.module("pathianApp.directives")
    .directive("benchmarkPerformanceTable", ["$parse", "$compile", "reportingGroupService",
        function($parse, $compile, reportingGroupService) {
            return {
                link: function(scope, elem, attrs) {
                    var model = $parse(attrs['benchmarkPerformanceTable'])(scope);

                    reportingGroupService.getBenchmarkPerformanceData(model, function(data) {
                        var $table = $(document.createElement('table'))
                            .attr('class', 'table table-striped dashboard-table');

                        $table.append('<tr><th>Group</th><th>Performance</th><th>Benchmark</th><th>Actual</th><th>Difference</th><th>Variance</th></tr>');
                        data.group_data.forEach(function(entry) {
                            $table.append('<tr><td>' + entry.name + '</td><td>' + entry.performance + '</td><td>' + entry.benchmark + '</td><td>' + entry.actual + '</td><td>' + entry.difference + '</td><td>' + entry.variance + '</td></tr>');
                        });
                        $table.append('<tr><td>Totals:</td><td>' + data.total_performance + '</td><td>' + data.total_benchmark_utility + '</td><td>' + data.total_reported_utility + '</td><td>' + data.total_difference + '</td><td>' + data.total_variance + '</td></tr>')

                        elem.empty();
                        elem.append($table);
                        $compile($table)(scope);
                    });
                }
            }
        },
    ]);