/**
 * Created by badams on 10/17/2014.
 */
angular.module('pathianApp.directives')
    .directive('equipmentConsumptionTable', ['$compile', 'reportingComponentService',
        function($compile, reportingComponentService) {
            return {
                scope: {
                    equipmentConsumptionTable: "="
                },
                terminal: true,
                link: function(scope, elem) {
                    // use the model to get the data for the equipment consumption table
                    reportingComponentService.getEquipmentReportTable(scope.equipmentConsumptionTable, function(data) {
                        var $table = $(document.createElement('table'))
                            .attr('class', 'table table-striped')
                            .attr('style', 'font-size:smaller');

                        $table.append("<tr><th></th><th>Monthly</th><th>Yearly</th></tr>");

                        $table.append("<tr><td>Benchmark Consumption:</td><td>" + data.benchmark_consumption_month + "</td>" +
                                      "<td>" + data.benchmark_consumption_year + "</td></tr>");
                        $table.append("<tr><td>Reported Consumption:</td><td>" + data.report_consumption_month + "</td>" +
                                      "<td>" + data.report_consumption_year + "</td></tr>");
                        $table.append("<tr><td>Difference:</td><td>" + data.difference_month + "</td>" +
                                      "<td>" + data.difference_year + "</td></tr>");
                        $table.append("<tr><td>Percent Difference:</td><td>" + data.percent_month + "</td>" +
                                      "<td>" + data.percent_year + "</td></tr>");
                        $table.append("<tr><td>Energy Cost Savings:</td><td>" + data.cost_month + "</td>" +
                                      "<td>" + data.cost_year + "</td></tr>");

                        elem.empty().append($table);
                        $compile($table)(scope);
                    });
                }
            };
        }
    ]);