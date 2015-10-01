angular.module("pathianApp.controllers")
    .controller("unknownJohnsonCtrl", [
        "$scope", "$routeParams", "$location",
        function($scope, $routeParams, $location) {
            $scope.global.linkpath = '#/data_mapping/unknown/johnson';
            $scope.siteId = $routeParams["siteId"];
            $scope.uploadResult = null;

            $scope.gridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/unknownJohnson",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
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
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                johnson_site_id: { type: "string"},
                                johnson_fqr: { type: "string" }
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
                columns: [
                    {field:"johnson_site_id",title:"Johnson Site Id"},
                    {field:"johnson_fqr",title:"Johnson FQR"}
                ]
            };

            $scope.fileUploadOptions = {
                url: "/api/data_mapping/unknownJohnson/upload",
                limitConcurrentUploads: 1,
                done: function() {
                    $(arguments[0].target).data("$scope").queue.length = 0;
                    $scope.uploadResult = arguments[1].result;
                }
            };
        }
    ]);


