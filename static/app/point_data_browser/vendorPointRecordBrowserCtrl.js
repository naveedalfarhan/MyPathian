angular.module("pathianApp.controllers")
    .controller("vendorPointRecordBrowserCtrl", [
        "$scope", "$rootScope", "$location", "$compile",
        function($scope, $rootScope, $location, $compile) {
            $rootScope.global.linkpath = "#/point_reporting/vendor_point_record_browser";

            $scope.selectedPoints = [];
            $scope.fromDate = new Date();
            $scope.toDate = new Date();

            var vendorFilter = function(element) {
                element.kendoDropDownList({
                    dataSource: ["fieldserver", "invensys", "johnson", "siemens"],
                    optionLabel: "--Select vendor--"
                })
            }

            $scope.pointListGridOptions = {
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {
                        title: "Vendor",
                        field: "vendor",
                        filterable: {
                            extra: false,
                            operators: {
                                string: {
                                    eq: "Is equal to"
                                }
                            },
                            ui: vendorFilter
                        }
                    },
                    {
                        title: "Sensor ID",
                        field: "sensor_id",
                        filterable: {
                            extra: false,
                            operators: {
                                string: {
                                    startswith: "Starts with",
                                    eq: "Is equal to"
                                }
                            }
                        }
                    },
                    {
                        title: "",
                        template: "<a class='k-button k-button-icontext k-grid-select' href='javascript:void(0)' ng-click='selectOrDeselectPoint($event)'><span class=''></span>#if(selected) {# Deselect #}else{# Select #}#</a>"
                    }
                ],
                editable: false,
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/vendor_points",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        }
                    },
                    schema: {
                        data: function (response) {
                            _.forEach(response.data, function(dataRecord) {
                                dataRecord.selected = _($scope.selectedPoints).any(function(x) {
                                    return dataRecord.vendor === x.vendor && dataRecord.sensor_id === x.sensor_id;
                                });
                            });
                            return response.data;
                        },
                        total: function (response) {
                            return response.total;
                        }
                    },
                    pageSize: 10,
                    serverPaging: true,
                    serverFiltering: true,
                    serverSorting: true
                }
            };

            $scope.setPointRecordListGridOptions = function() {
                // the python library parseqs doesn't properly recognize "varname[]=1&varname[]=2&varname[]=3" as array items,
                // it interprets this as three separate settings to the varname dictionary with the key "". to combat this,
                // the selectedPoints array is put into an object with the keys equal to the array indices. this will generate
                // a string such as "varname[0]=1&varname[1]=2&varname[2]=3" which is handled correctly.

                var pointObj = {};
                _($scope.selectedPoints).forEach(function(point, index) {
                    pointObj[index] = {
                        vendor:  point.vendor,
                        sensor_id: point.sensor_id
                    };
                });

                $scope.pointRecordListGridOptions = {
                    scrollable: false,
                    filterable: false,
                    sortable: false,
                    pageable: true,
                    columns: [
                        {
                            title: "Vendor",
                            field: "vendor"
                        },
                        {
                            title: "Sensor ID",
                            field: "sensor_id"
                        },
                        {
                            title: "UTC Timestamp",
                            template: "#=kendo.toString(kendo.parseDate(utc_timestamp, 'ddd, dd MMM yyyy HH:mm:ss'), 'u')#"
                        },
                        {
                            title: "Value",
                            field: "value"
                        }
                    ],
                    editable: false,
                    dataSource: {
                        transport: {
                            read: {
                                url: "/api/equipment/vendor_records",
                                dataType: "json",
                                contentType: "application/json",
                                type: "POST",
                                data: {
                                    points: pointObj,
                                    startDate: Date.parse($scope.fromDate) / 1000,
                                    endDate: Date.parse($scope.toDate) / 1000
                                }
                            }
                        },
                        schema: {
                            data: function (response) {
                                return response.data;
                            },
                            total: function (response) {
                                return response.total;
                            }
                        },
                        pageSize: 50,
                        serverPaging: true,
                        serverFiltering: true,
                        serverSorting: true
                    }
                };
            };

            $scope.buildPointRecordListGrid = function() {
                var gridContainer = $("#pointRecordDataBrowserGridContainer");
                gridContainer.empty();
                $scope.setPointRecordListGridOptions();
                gridContainer.append("<div kendo-grid k-options='pointRecordListGridOptions'></div>");
                $compile(gridContainer)($scope);
            };

            $scope.selectOrDeselectPoint = function(e) {
                var kendoGrid = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid");
                var item = kendoGrid.dataItem($(e.currentTarget).closest("[data-uid]"));

                var pointListIndex = -1;
                for (var i = 0; i < $scope.selectedPoints.length; ++i) {
                    var selectedPoint = $scope.selectedPoints[i];
                    if (selectedPoint.vendor === item.vendor && selectedPoint.sensor_id === item.sensor_id) {
                        pointListIndex = i;
                        break;
                    }
                }

                if (item.selected && pointListIndex > -1) {
                    $scope.selectedPoints.splice(pointListIndex, 1);
                    item.selected = false;
                } else if (!item.selected && pointListIndex === -1) {
                    $scope.selectedPoints.push({vendor: item.vendor, sensor_id: item.sensor_id});
                    $scope.selectedPoints.sort();
                    item.selected = true;
                }

                kendoGrid.refresh();
            };

            $scope.deselectPoint = function(point) {
                var pointListIndex = -1;
                for (var i = 0; i < $scope.selectedPoints.length; ++i) {
                    var selectedPoint = $scope.selectedPoints[i];
                    if (selectedPoint.vendor === point.vendor && selectedPoint.sensor_id === point.sensor_id) {
                        pointListIndex = i;
                        break;
                    }
                }

                if (pointListIndex > -1) {
                    $scope.selectedPoints.splice(pointListIndex, 1);


                    var kendoGrid = $("#pointDataBrowserGrid").data("kendoGrid");
                    var item = _(kendoGrid.dataSource.data()).find(function(x) {
                        return x.vendor === point.vendor && x.sensor_id === point.sensor_id;
                    });
                    if (item) {
                        item.selected = false;
                        kendoGrid.refresh();
                    }

                }
            };

            $scope.submit = function() {
                $scope.buildPointRecordListGrid();
            }
        }
    ]);