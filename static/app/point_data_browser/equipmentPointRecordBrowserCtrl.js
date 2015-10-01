angular.module("pathianApp.controllers")
    .controller("equipmentPointRecordBrowserCtrl", [
        "$scope", "$rootScope", "$location", "$compile",
        function($scope, $rootScope, $location, $compile) {
            $rootScope.global.linkpath = "#/point_reporting/equipment_point_record_browser";

            $scope.selectedPoints = [];
            $scope.fromDate = new Date();
            $scope.toDate = new Date();

            $scope.pointListGridOptions = {
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {
                        title: "Syrx num",
                        field: "syrx_num",
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
                        template: "<a class='k-button k-button-icontext k-grid-select' href='javascript:void(0)' ng-click='selectOrDeselectSyrxNum($event)'><span class=''></span>#if(selected) {# Deselect #}else{# Select #}#</a>"
                    }
                ],
                editable: false,
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/equipment_points",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        parameterMap: function (options, operation) {
                            return options;
                        }
                    },
                    schema: {
                        data: function (response) {
                            _.forEach(response.data, function(dataRecord) {
                                dataRecord.selected = _($scope.selectedPoints).any(function(x) { return dataRecord.syrx_num === x;});
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

                var syrxNumObj = {};
                _($scope.selectedPoints).forEach(function(syrxNum, index) {
                    syrxNumObj[index] = syrxNum;
                });

                $scope.pointRecordListGridOptions = {
                    scrollable: false,
                    filterable: false,
                    sortable: false,
                    pageable: true,
                    columns: [
                        {
                            title: "Syrx num",
                            field: "syrx_num"
                        },
                        {
                            title: "Timestamp",
                            template: "#=kendo.toString(kendo.parseDate(date, 'ddd, dd MMM yyyy HH:mm:ss'), 'u')#"
                        },
                        {
                            title: "Value",
                            field: "value"
                        },
                        {
                            title: "Weather timestamp",
                            template: "#=kendo.toString(kendo.parseDate(weather.datetimeutc, 'ddd, dd MMM yyyy HH:mm:ss'), 'u')#"
                        },
                        {
                            title: "Temp",
                            field: "weather.temp"
                        },
                        {
                            title: "Dew pt",
                            field: "weather.dewpt"
                        },
                        {
                            title: "Enth",
                            template: "#=kendo.toString(weather.enthalpy, 'n2')#"
                        },
                        {
                            title: "Alt",
                            field: "weather.alt"
                        }
                    ],
                    editable: false,
                    dataSource: {
                        transport: {
                            read: {
                                url: "/api/equipment/equipment_point_records",
                                dataType: "json",
                                contentType: "application/json",
                                type: "POST",
                                data: {
                                    syrxNums: syrxNumObj,
                                    startDate: Date.parse($scope.fromDate) / 1000,
                                    endDate: Date.parse($scope.toDate) / 1000
                                }
                            },
                            parameterMap: function (options, operation) {
                                return options;
                            }
                        },
                        schema: {
                            data: function (response) {
                                _.forEach(response.data, function(dataRecord) {
                                    dataRecord.selected = _($scope.selectedPoints).any(function(x) { return dataRecord.syrx_num === x;});
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
            };

            $scope.buildPointRecordListGrid = function() {
                var gridContainer = $("#pointRecordDataBrowserGridContainer");
                gridContainer.empty();
                $scope.setPointRecordListGridOptions();
                gridContainer.append("<div kendo-grid k-options='pointRecordListGridOptions'></div>");
                $compile(gridContainer)($scope);
            };

            $scope.selectOrDeselectSyrxNum = function(e) {
                var kendoGrid = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid");
                var item = kendoGrid.dataItem($(e.currentTarget).closest("[data-uid]"));

                var syrxNumExistsInList = _($scope.selectedPoints).any(function(x) { return item.syrx_num === x;});

                if (item.selected && syrxNumExistsInList) {
                    var itemIndex = _($scope.selectedPoints).indexOf(item.syrx_num);
                    $scope.selectedPoints.splice(itemIndex, 1);
                    item.selected = false;
                } else if (!item.selected && !syrxNumExistsInList) {
                    $scope.selectedPoints.push(item.syrx_num);
                    $scope.selectedPoints.sort();
                    item.selected = true;
                }

                kendoGrid.refresh();
            };

            $scope.deselectSyrxNum = function(syrxNum) {
                var syrxNumExistsInList = _($scope.selectedPoints).any(function(x) { return syrxNum === x;});
                if (syrxNumExistsInList) {
                    var itemIndex = _($scope.selectedPoints).indexOf(syrxNum);
                    $scope.selectedPoints.splice(itemIndex, 1);


                    var kendoGrid = $("#pointDataBrowserGrid").data("kendoGrid");
                    var item = _(kendoGrid.dataSource.data()).find(function(x) {return x.syrx_num === syrxNum; });
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