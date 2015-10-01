angular.module("pathianApp.directives")
    .directive("reportingIntensityChart", ["$parse", "$timeout", "$compile", "reportingGroupService", "reportingNaicsService", "reportingSicService", "reportingComponentService",
        function($parse, $timeout, $compile, reportingGroupService, reportingNaicsService, reportingSicService, reportingComponentService) {
            return {
                scope: {
                    difference: "=",
                    reportingIntensityChart: "=",
                    reportType: "="
                },
                link: function(scope, elem, attrs){

                    scope.$watchCollection("reportingIntensityChart", rebuildChart);

                    function rebuildChart() {
                        var model = scope["reportingIntensityChart"];
                        var reportType = scope["reportType"];

                        // if the model comes in null or undefined, don't show the chart
                        if (!model) {
                            elem.empty();
                            return false;
                        }

                        var service;
                        if (reportType === "naics")
                            service = reportingNaicsService;
                        else if (reportType === "sic")
                            service = reportingSicService;
                        else if (reportType === 'component')
                            service = reportingComponentService;
                        else
                            service = reportingGroupService;
                        service.getIntensityData(model, function (resource) {

                            var chartData = [];
                            for (var j = 0; j < resource.data.length; ++j) {
                                chartData.push({
                                    data: resource.data[j].data,
                                    name: resource.data[j].name
                                })
                            }


                            scope.intensityChartOptions = {
                                title: {
                                    text: resource.title
                                },
                                legend: {
                                    visible: true,
                                    position: "bottom",
                                    labels: {
                                        template: "#: text #"
                                    }
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
                                        text: resource.x_axis_label
                                    }
                                },
                                yAxis: {
                                    labels: {
                                        format: '{0}'
                                    },
                                    title: {
                                        text: resource.y_axis_label
                                    }
                                }
                            };

                            var $kendoChartDiv = $(document.createElement("div"))
                                .attr("kendo-chart", "")
                                .attr("k-options", "intensityChartOptions");

                            elem.empty().append($kendoChartDiv);

                            $compile($kendoChartDiv)(scope);
                        });
                    }

                }
            }
        }
    ]);