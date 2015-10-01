/**
 * Created by badams on 10/2/2014.
 */
angular.module("pathianApp.directives")
    .directive("componentComparisonTable", ["$parse", "$compile", "reportingComponentService",
        function($parse, $compile, reportingComponentService) {
            return {
                scope: {
                    componentComparisonTable: "="
                },
                terminal: true,
                link: function(scope, elem) {

                    scope.$watchCollection("componentComparisonTable", rebuildTable);

                    function rebuildTable() {
                        reportingComponentService.getComparisonTableData(scope.componentComparisonTable, function(data) {
                            var $table = $(document.createElement("table"))
                                .attr("class", "table table-striped");

                            $table.append("<tr>" +
                                            "<th>Equipment Name</th>" +
                                            "<th>Component ID</th><th>Description</th><th>Units</th>" +
                                            "<th>BIC % Diff</th><th>Energy/Hour Diff</th><th>Energy/Year Diff</th>" +
                                            "<th>$ Hour</th><th>$ Annual</th>" +
                                          "</tr>");

                            data.rows.forEach(function(row) {
                                var rowClass = '';
                                if (row.class === 'bic')
                                    rowClass = 'bic';

                                $table.append("<tr class='" + rowClass + "'>" +
                                                "<td>" + row.equipment_name + "</td>" +
                                                "<td>" + row.component_id + "</td>" +
                                                "<td>" + row.description + "</td>" +
                                                "<td>" + row.units + "</td>" +
                                                "<td>" + row.diff + "</td>" +
                                                "<td>" + row.hour_diff + "</td>" +
                                                "<td>" + row.year_diff + "</td>" +
                                                "<td>" + row.hour_cost_diff + "</td>" +
                                                "<td>" + row.year_cost_diff + "</td>" +
                                              "</tr>");
                            });

                            elem.empty().append($table);

                            $compile($table)(scope);

                        });
                    }
                }
            }
        }
    ]);