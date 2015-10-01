angular.module("pathianApp.directives")
    .directive("textReport", ["$parse", "$compile", "textReportService",
        function($parse, $compile, textReportService){
            return {
                scope: {
                    textReport: "=",
                    reportType: "="
                },
                link: function(scope, elem, attrs) {

                    scope.$watchCollection("textReport", generateReport);

                    function generateReport() {

                        var model = scope["textReport"];
                        var reportType = scope["reportType"];

                        // if the model is undefined or null, don't generate a new report
                        if (!model) {
                            elem.empty();
                            return false;
                        }

                        var method;
                        if (reportType === 'naics') {
                            method = textReportService.getNaicsReport;
                        }
                        else if (reportType === 'sic') {
                            method = textReportService.getSicReport;
                        }
                        else {
                            method = textReportService.getGroupReport;
                        }

                        method(model, function (data) {
                            elem.empty();

                            var electric_units = data.electric_units;
                            var gas_units = data.gas_units;
                            var btu_units = data.btu_units;

                            var $mainTable = $(document.createElement("table"))
                                .attr("class", "table table-striped");
                            $mainTable.append("<tr><th>" + data.organization_column_title + "</th><th>Utility (" + btu_units + ")</th><th>Reported (" + btu_units + ")</th><th>Benchmark (" + btu_units + ")</th><th>Difference (" + btu_units + ")</th><th>% Change</th><th>Energy Savings ($)</th></tr>");
                            data.main_table.organization_data.forEach(function (entry) {
                                $mainTable.append("<tr><td>" + entry.organization_name + "</td><td>" + entry.utility + "</td><td>" + entry.reported_utility + "</td><td>" + entry.benchmark_utility + "</td><td>" + entry.difference + "</td><td>" + entry.change + "</td><td>" + entry.savings + "</td></tr>");

                            });
                            $mainTable.append("<tr><td>Grand Total</td><td>" + data.main_table.total_data.utility + "</td><td>" + data.main_table.total_data.reported_utility + "</td><td>" + data.main_table.total_data.benchmark_utility + "</td><td>" + data.main_table.total_data.difference + "</td><td>" + data.main_table.total_data.change + "</td><td>" + data.main_table.total_data.savings + "</td></tr>");

                            elem.append($mainTable);
                            $compile($mainTable)(scope);

                            data.detailed_tables.forEach(function (entry) {
                                var $groupTableHeader = $(document.createElement("h3"));
                                $groupTableHeader.append(entry.organization_name);
                                var $groupTable = $(document.createElement("table"))
                                    .attr("class", "table table-striped");
                                $groupTable.append("<tr><th>Account</th><th>Utility (" + btu_units + ")</th><th>Reported (" + btu_units + ")</th><th>Benchmark (" + btu_units + ")</th><th>Difference (" + btu_units + ")</th><th>% Change</th><th>Energy Savings ($)</th></tr>");
                                entry.data.forEach(function (dataItem) {
                                    $groupTable.append("<tr><td>" + dataItem.account_name + "</td><td>" + dataItem.utility + "</td><td>" + dataItem.reported_utility + "</td><td>" + dataItem.benchmark_utility + "</td><td>" + dataItem.difference + "</td><td>" + dataItem.change + "</td><td>" + dataItem.savings + "</td></tr>");
                                });
                                $groupTable.append("<tr><td>Totals:</td><td>" + entry.accounts_utility_total + "</td><td>" + entry.accounts_reported_total + "</td><td>" + entry.accounts_benchmark_total + "</td><td>" + entry.accounts_difference_total + "</td><td>" + entry.accounts_change_total + "</td><td>" + entry.accounts_savings_total + "</td></tr>");

                                elem.append($groupTableHeader);
                                elem.append($groupTable);
                                $compile($groupTableHeader)(scope);
                                $compile($groupTable)(scope);

                                if (model.account_type !== 'gas') {
                                    var $electricAccountsTableHeader = $(document.createElement("h3"));
                                    $electricAccountsTableHeader.append(entry.organization_name + " (Electric)");
                                    var $electricAccountsTable = $(document.createElement("table"))
                                        .attr("class", "table table-striped");
                                    $electricAccountsTable.append("<tr><th>Account</th><th>Utility (" + electric_units + ")</th><th>Reported (" + electric_units + ")</th><th>Benchmark (" + electric_units + ")</th><th>Difference (" + electric_units + ")</th><th>% Change</th><th>Energy Savings ($)</th></tr>");
                                    entry.electric_accounts.data.forEach(function (dataItem) {
                                        $electricAccountsTable.append("<tr><td>" + dataItem.account_name + "</td><td>" + dataItem.utility + "</td><td>" + dataItem.reported_utility + "</td><td>" + dataItem.benchmark_utility + "</td><td>" + dataItem.difference + "</td><td>" + dataItem.change + "</td><td>" + dataItem.savings + "</td></tr>");
                                    });
                                    $electricAccountsTable.append("<tr><td>Totals:</td><td>" + entry.electric_accounts.total_electric_utility + "</td><td>" + entry.electric_accounts.total_electric_reported + "</td><td>" + entry.electric_accounts.total_electric_benchmark + "</td><td>" + entry.electric_accounts.total_electric_difference + "</td><td>" + entry.electric_accounts.total_electric_change + "</td><td>" + entry.electric_accounts.total_electric_savings + "</td></tr>");

                                    elem.append($electricAccountsTableHeader);
                                    elem.append($electricAccountsTable);
                                    $compile($electricAccountsTableHeader)(scope);
                                    $compile($electricAccountsTable)(scope);
                                }

                                if (model.account_type != 'electric') {
                                    var $gasAccountsTableHeader = $(document.createElement("h3"));
                                    $gasAccountsTableHeader.append(entry.organization_name + " (Gas)");
                                    var $gasAccountsTable = $(document.createElement("table"))
                                        .attr("class", "table table-striped");
                                    $gasAccountsTable.append("<tr><th>Account</th><th>Utility (" + gas_units + ")</th><th>Reported (" + gas_units + ")</th><th>Benchmark (" + gas_units + ")</th><th>Difference (" + gas_units + ")</th><th>% Change</th><th>Energy Savings ($)</th></tr>");
                                    entry.gas_accounts.data.forEach(function (dataItem) {
                                        $gasAccountsTable.append("<tr><td>" + dataItem.account_name + "</td><td>" + dataItem.utility + "</td><td>" + dataItem.reported_utility + "</td><td>" + dataItem.benchmark_utility + "</td><td>" + dataItem.difference + "</td><td>" + dataItem.change + "</td><td>" + dataItem.savings + "</td></tr>");
                                    });
                                    $gasAccountsTable.append("<tr><td>Totals:</td><td>" + entry.gas_accounts.total_gas_utility + "</td><td>" + entry.gas_accounts.total_gas_reported + "</td><td>" + entry.gas_accounts.total_gas_benchmark + "</td><td>" + entry.gas_accounts.total_gas_difference + "</td><td>" + entry.gas_accounts.total_gas_change + "</td><td>" + entry.gas_accounts.total_gas_savings + "</td></tr>");

                                    elem.append($gasAccountsTableHeader);
                                    elem.append($gasAccountsTable);
                                    $compile($gasAccountsTableHeader)(scope);
                                    $compile($gasAccountsTable)(scope);
                                }

                            });
                        });
                    }
                }
            }
        }
    ]);