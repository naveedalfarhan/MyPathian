angular.module("pathianApp.controllers")
    .controller("dataMappingJohnsonCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "contactService",
        function ($scope, $rootScope, $location, $routeParams, contactService) {
            $scope.global.linkpath = '#/data_mapping/johnson';

            var handleGridError = function() {
                var errorMessageDiv = $(document.createElement("div"))
                    .addClass("k-widget k-tooltip k-tooltip-validation k-invalid-msg")
                    .css({margin: "0.5em", display: "block"})
                    .attr("data-for", "syrx_num")
                    .attr("role", "alert");
                var warningSpan = $(document.createElement("span"))
                    .addClass("k-icon k-warning");
                var calloutDiv = $(document.createElement("div"))
                    .addClass("k-callout k-callout-n");

                errorMessageDiv
                    .append(warningSpan)
                    .append("syrx_num is not valid")
                    .append(calloutDiv);

                var gridDiv = $("[data-name='johnsonGrid']");
                var row = gridDiv.find("tr.k-grid-edit-row");
                var cell = row.children("[data-container-for='syrx_num']");
                cell.append(errorMessageDiv);
            };

            $scope.gridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/johnson",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        update: {
                            url: function (options) {
                                return "/api/data_mapping/johnson/" + options.id;
                            },
                            dataType: "json",
                            contentType: "application/json",
                            type: "PUT"
                        },
                        destroy: {
                            url: function (options) {
                                return "/api/data_mapping/johnson/" + options.id;
                            },
                            dataType: "json",
                            contentType: "application/json",
                            type: "DELETE"
                        },
                        create: {
                            url: "/api/data_mapping/johnson",
                            dataType: "json",
                            contentType: "application/json",
                            type: "POST"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    error: handleGridError,
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                id: { type: "string" },
                                syrx_num: { type: "string", validation: { required: true } },
                                johnson_site_id: { type: "string", validation: { required: true } },
                                johnson_fqr: { type: "string", validation: { required: true } }
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                },
                scrollable: false,
                filterable: false,
                sortable: false,
                pageable: true,
                toolbar: [{template:"<a class='k-button k-button-icontext k-grid-add'><span class='k-icon k-add'></span>Add point</a>"}],
                columns: [
                    {field:"syrx_num",title:"Syrx num"},
                    {field:"johnson_site_id",title:"Johnson Site Id"},
                    {field:"johnson_fqr",title:"Johnson FQR"},
                    {
                        command: ["edit", "destroy"]
                    }
                ],
                editable: "inline"
            };
        }
    ]);