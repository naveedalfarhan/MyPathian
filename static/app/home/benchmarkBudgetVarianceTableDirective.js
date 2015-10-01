angular.module('pathianApp.directives')
    .directive("benchmarkBudgetVarianceTable", ["$parse", "$compile", "reportingGroupService",
        function($parse, $compile, reportingGroupService) {
            return {
                link: function(scope, elem, attrs) {
                    var model = $parse(attrs['benchmarkBudgetVarianceTable'])(scope);

                    reportingGroupService.getBenchmarkBudgetVarianceData(model, function(data) {
                        var $table = $(document.createElement("table"))
                            .attr("class", "table table-striped dashboard-table");

                        $table.append("<tr><th>Account</th><th>Annual Budget</th><th>Consumption To Date</th><th>Variance</th><th>Budget Variance</th></tr>");
                        data.forEach(function(entry){
                            $table.append("<tr><td>" + entry.name + "</td><td>" + entry.annual_budget + "</td><td>" + entry.consumption + "</td><td>" + entry.variance + "</td><td>" + entry.budget_variance + "</td></tr>");
                        });

                        elem.empty();
                        elem.append($table);

                        $compile($table)(scope);
                    });
                }
            }
        }
    ]);