/**
 * Created by badams on 9/30/2014.
 */
angular.module("pathianApp.directives")
    .directive("componentConsumptionChart", ["$parse", "$compile", "reportingComponentService",
        function($parse, $compile, reportingComponentService) {
            return {
                scope: {
                    "chartModel": "="
                },
                terminal: true,
                link: function(scope, elem) {
                    scope.$watchCollection("chartModel", rebuildChart);

                    function rebuildChart() {
                        reportingComponentService.getComparisonData(scope.chartModel, function (data) {
                            // generate chart
                            scope.chartOptions = {
                                title: {
                                    text: data.title
                                },
                                legend: {
                                    visible: true,
                                    position: 'bottom'
                                },
                                chartArea: {
                                    background: ''
                                },
                                series: data.data,
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
                                        text: data.x_axis_label
                                    }
                                },
                                yAxis: {
                                    labels: {
                                        format: '{0}'
                                    },
                                    title: {
                                        text: data.y_axis_label
                                    }
                                }
                            };

                            var $kendoChartDiv = $(document.createElement("div"))
                                .attr("kendo-chart", "")
                                .attr("k-options", "chartOptions");

                            elem.empty().append($kendoChartDiv);

                            $compile($kendoChartDiv)(scope);
                        });
                    }
                }
            }
        }
    ]);