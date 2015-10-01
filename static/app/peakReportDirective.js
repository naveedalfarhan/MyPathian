angular.module("pathianApp.directives")
    .directive("peakReport", ["$parse", "$compile", "reportingGroupService", "reportingNaicsService", "reportingSicService",
        function($parse, $compile, reportingGroupService, reportingNaicsService, reportingSicService) {
            return {
                scope:{
                    peakReport: "=",
                    reportType: "="
                },
                link: function(scope, elem, attrs) {

                    scope.$watchCollection('peakReport', generateReport);


                    function generateReport() {
                        var model = scope["peakReport"];
                        var reportType = scope["reportType"];

                        // if the model is null or undefined, don't generate the report
                        if (!model) {
                            elem.empty();
                            return false;
                        }

                        var service;
                        if (reportType === 'naics') {
                            service = reportingNaicsService;
                        }
                        else if (reportType === 'sic') {
                            service = reportingSicService;
                        }
                        else {
                            service = reportingGroupService;
                        }

                        service.peakReport(model, function (data) {
                            var count = 0;
                            scope.tempChartOptions = [];
                            scope.demandChartOptions = [];

                            elem.empty();

                            data.forEach(function (entry) {
                                elem.append("<h4>" + entry.name + "</h4>");
                                scope.tempChartOptions.push({
                                    title: {
                                        text: entry.date
                                    },
                                    legend: {
                                        visible: true,
                                        position: 'top'
                                    },
                                    chartArea: {
                                        background: ''
                                    },
                                    series: [
                                        {
                                            name: "Hourly Temperature",
                                            data: entry.temp_data
                                        }
                                    ],
                                    seriesDefaults: {
                                        type: 'scatterLine',
                                        width: 3,
                                        style: 'smooth',
                                        markers: {
                                            size: 1
                                        }
                                    },
                                    xAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: 'Hour'
                                        }
                                    },
                                    yAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: 'Temperature (F)'
                                        }
                                    }
                                });

                                var $tempChartContainer = $(document.createElement("div"))
                                    .attr("class", "col-md-6");
                                var $tempChart = $(document.createElement("div"))
                                    .attr("kendo-chart", "")
                                    .attr("k-options", "tempChartOptions[" + count + "]");

                                $tempChartContainer.append($tempChart);
                                elem.append($tempChartContainer);

                                scope.demandChartOptions.push({
                                    title: {
                                        text: entry.date
                                    },
                                    legend: {
                                        visible: true,
                                        position: 'top'
                                    },
                                    chartArea: {
                                        background: ''
                                    },
                                    series: [
                                        {
                                            name: "Hourly Consumption Rate",
                                            data: entry.demand_data
                                        }
                                    ],
                                    seriesDefaults: {
                                        type: 'scatterLine',
                                        width: 3,
                                        style: 'smooth',
                                        markers: {
                                            size: 1
                                        }
                                    },
                                    xAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: 'Hour'
                                        }
                                    },
                                    yAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: 'Demand (kW)'
                                        }
                                    }
                                });

                                var $demandChartContainer = $(document.createElement("div"))
                                    .attr("class", "col-md-6");
                                var $demandChart = $(document.createElement("div"))
                                    .attr("kendo-chart", "")
                                    .attr("k-options", "demandChartOptions[" + count + "]");

                                $demandChartContainer.append($demandChart);
                                elem.append($demandChartContainer);

                                var $table = $(document.createElement("table"))
                                    .attr("class", "table table-striped");

                                $table.append("<tr><th>kW</th><th>Date</th></tr>");

                                entry.demand_table_data.forEach(function (record) {
                                    $table.append("<tr><td>" + record[0] + "</td><td>" + record[1] + "</td></tr>");
                                });

                                elem.append($table);

                                $compile($tempChartContainer)(scope);
                                $compile($tempChart)(scope);
                                $compile($demandChartContainer)(scope);
                                $compile($demandChart)(scope);
                                $compile($table)(scope);
                                count++;
                            });
                        });
                    }
                }
            }
        }
    ]);