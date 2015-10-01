angular.module("pathianApp.directives")
    .directive("reportingConsumptionChart", ["$parse", "$timeout", "$compile", "reportingGroupService", "reportingNaicsService", "reportingSicService", "reportingComponentService",
        function($parse, $timeout, $compile, reportingGroupService, reportingNaicsService, reportingSicService, reportingComponentService) {
            return {
                scope: {
                    difference: "=",
                    reportingConsumptionChart: "="
                },
                link: function(scope, elem, attrs){

                    scope.$watchCollection("reportingConsumptionChart", rebuildContents);

                    function rebuildContents() {
                        var diff = scope["difference"];
                        var model = scope["reportingConsumptionChart"];

                        // make sure model is defined before continuing
                        if (!model) {
                            elem.empty();
                            return false;
                        }


                        var service;
                        if (attrs['reportType'] === "naics")
                            service = reportingNaicsService;
                        else if (attrs['reportType'] === "sic")
                            service = reportingSicService;
                        else if (attrs['reportType'] === "component")
                            service = reportingComponentService;
                        else
                            service = reportingGroupService;
                        service.getTotalEnergyData(model, function (resource) {

                            var chartData = [];
                            if (!diff)
                                chartData = resource[0]['consumption-chart'];
                            else
                                chartData = resource[0]['difference-chart'];


                            scope.consumptionChartOptions = [
                                {
                                    title: {
                                        text: resource[0].title
                                    },
                                    legend: {
                                        visible: true,
                                        position: 'top'
                                    },
                                    chartArea: {
                                        background: ''
                                    },
                                    series: chartData,
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
                                            text: resource[0].x_axis_label
                                        }
                                    },
                                    yAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: resource[0].y_axis_label
                                        }
                                    }
                                },
                                {
                                    title: {
                                        text: resource[0].title
                                    },
                                    legend: {
                                        visible: true,
                                        position: 'top'
                                    },
                                    chartArea: {
                                        background: ''
                                    },
                                    series: chartData,
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
                                            text: resource[0].x_axis_label
                                        }
                                    },
                                    yAxis: {
                                        labels: {
                                            format: '{0}'
                                        },
                                        title: {
                                            text: resource[0].y_axis_label
                                        }
                                    }
                                }
                            ];
                            var options = "consumptionChartOptions[0]";
                            if (diff)
                                options = "consumptionChartOptions[1]";

                            var $kendoChartDiv = $(document.createElement("div"))
                                .attr("kendo-chart", "")
                                .attr("k-options", options);

                            elem.empty().append($kendoChartDiv);

                            $compile($kendoChartDiv)(scope);
                        });

                    };

                }
            }
        }
    ]);