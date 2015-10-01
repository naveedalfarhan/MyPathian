angular.module("pathianApp.directives")
    .directive("reportingEnergySummaryTable", ["$parse", "$timeout", "$compile", "reportingGroupService",
        function($parse, $timeout, $compile, reportingGroupService) {
            return {
                scope: {
                    reportingEnergySummaryTable: "=",
                },
                link: function(scope, elem) {

                    // use the model to get the data for the equipment consumption table
                    scope.$watchCollection("reportingEnergySummaryTable", rebuildTable);
                    function rebuildTable() {
                    var service = reportingGroupService;
                    service.GetEnergySummaryData(scope.reportingEnergySummaryTable, function(data) {

                        var $table = $(document.createElement('table'))
                                    .attr('class', 'table-bordered')
                                    .attr('style', 'font-size:smaller');

                        $table.append("<tr><th>Group</th><th>Utility (MMBtus)</th><th>Reported (MMBtus)</th><th>Benchmark (MMBtus)</th><th>Difference (MMBtus)</th><th>% Change</th><th>Energy Savings ($)</th></tr>");

                        for(var key in data.group_data) {
                        $table.append("<tr><td>"+ data.group_data[key].entity +
                                      "</td><td>" + data.group_data[key].utility +
                                      "</td><td>" + data.group_data[key].reported +
                                      "</td><td>" + data.group_data[key].benchmark +
                                      "</td><td>" + data.group_data[key].difference +
                                      "</td><td>" + data.group_data[key].change +
                                      "</td><td>" + data.group_data[key].savings + "</td></tr>");
                        }

                        elem.empty().append($table);
                        $compile($table)(scope);
                    });
                    }
                }
            }
        }
    ]);