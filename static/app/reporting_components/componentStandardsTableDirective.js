/**
 * Created by badams on 9/16/2014.
 */


angular.module('pathianApp.directives')
    .directive('componentStandardsTable', ["$compile", "reportingComponentService",
        function($compile, reportingComponentService){
            return {
                scope: {
                    componentStandardsTable: "="
                },
                link: function(scope, elem) {
                    scope.$watchCollection("componentStandardsTable", rebuildTable);

                    function rebuildTable() {
                        var model = scope["componentStandardsTable"];

                        elem.empty();

                        // if the model comes in null or undefined don't show the table
                        if (!model) {
                            return false;
                        }

                        var $table = $(document.createElement("table"))
                            .attr('class', 'table table-striped');

                        // build the header
                        $table.append("<tr><th>Component Point</th><th>Description</th><th>Units</th><th>PPSN</th><th>BIC</th><th>% Difference</th></tr>");

                        reportingComponentService.getStandardsTableData(model, function(response) {
                            // create a new row for each entry
                            response.forEach(function(row) {
                                $table.append("<tr><td>" + row.component + "</td><td>" + row.description + "</td><td>" + row.units + "</td><td>" + row.ppsn + "</td><td>" + row.bic + "</td><td>" + row.diff + "</td></tr>");
                            });
                        });

                        elem.append($table);

                        $compile($table)(scope);
                    }
                }
            };
        }
    ]);