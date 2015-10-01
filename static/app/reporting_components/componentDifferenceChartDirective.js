/**
 * Created by badams on 10/6/2014.
 */
angular.module('pathianApp.directives')
    .directive('componentDifferenceChart', ["$compile", "reportingComponentService",
        function($compile, reportingComponentService) {
            return {
                scope: {
                    chartModel: "=",
                    type: "@"
                },
                terminal: true,
                link: function(scope, elem) {

                    scope.$watchCollection("chartModel", rebuildCharts);

                    function rebuildCharts() {
                        var func;
                        if (scope.type === 'equipment')
                            func = reportingComponentService.getEquipmentReport;
                        else
                            func = reportingComponentService.getDifferenceData;
                        func(scope.chartModel, function(data) {
                            // generate first chart
                            scope.consumptionChartOptions = {
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
                                series: data.consumption_data,
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

                            var $kendoConsumptionWrapper = $(document.createElement("div"))
                                .attr("class", "col-md-6");
                            var $kendoConsumptionChartDiv = $(document.createElement("div"))
                                .attr("kendo-chart", "")
                                .attr("k-options", "consumptionChartOptions");

                            $kendoConsumptionWrapper.append($kendoConsumptionChartDiv);

                            elem.empty().append($kendoConsumptionWrapper);

                            // generate second chart
                            scope.differenceChartOptions = {
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
                                series: data.difference_data,
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

                            var $kendoDifferenceWrapper = $(document.createElement("div"))
                                .attr("class", "col-md-6");

                            var $kendoDifferenceChartDiv = $(document.createElement("div"))
                                .attr("kendo-chart", "")
                                .attr("k-options", "differenceChartOptions");

                            $kendoDifferenceWrapper.append($kendoDifferenceChartDiv);
                            elem.append($kendoDifferenceWrapper);

                            // compile the two charts
                            $compile($kendoConsumptionWrapper)(scope);
                            $compile($kendoDifferenceWrapper)(scope);
                        });
                    }
                }
            }
        }
    ]);