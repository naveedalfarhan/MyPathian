angular.module("pathianApp.controllers")
    .controller("testDataDumpCtrl", ["$scope", "$http",
        function($scope, $http) {
            $scope.models = {
                johnson: "Site ID,FQR,Timestamp,Value,Reliability\n330938,JOHNSON-19F0FEA:GSH-NCE16/FCB.Local Application.PH-T,8/6/2014 1:00 PM,78.6,Reliable,\n",
                fieldserver: '{"cc14153300_Offsets_0000-0009": "44.000000 ,44.599998 ,3276.699951 ,73.500000 ,33.599998 ,34044.445312 ,33.299999 ,33.299999 ,32.900002 ,50.200001"}\n',
                invensys: "2014-05-06T11:45:00.216-04:00,Bethesda Oak,Ch6 East,CH6_ChilledWaterFlow_ID644,981.4877319335938\n" +
                          "2014-05-06T11:45:00.216-04:00,Bethesda Oak,Ch6 East,CH6_SupplyTemp_ID645,46.6879997253418\n" +
                          "2014-05-06T11:45:00.216-04:00,Bethesda Oak,Ch6 East,CH6_ReturnTemp_ID646,49.784000396728516\n" +
                          "2014-05-06T11:45:00.216-04:00,Bethesda Oak,Ch6 East,CH6_Load_Tons_ID647,126.71324157714844\n"
            };

            $scope.responses = {
                johnson: "",
                fieldserver: "",
                invensys: ""
            };

            $scope.submitJohnson = function() {
                $scope.responses.johnson = "Submitting...";
                $http({
                    method: "post",
                    url: "/api/data_dump/johnson",
                    headers: {"Content-Type": "multipart/form-data; boundary=----testboundary"},
                    data: "------testboundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"file\"\r\nContent-type: plain/text\r\n\r\n" + $scope.models.johnson + "\r\n------testboundary--\r\n",
                    transformRequest: angular.identity
                }).success(function(data, status, headers, config) {
                    $scope.responses.johnson = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                }).error(function(data, status, headers, config) {
                    $scope.responses.johnson = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                });
            };

            $scope.submitFieldserver = function() {
                $scope.responses.fieldserver = "Submitting...";
                $http({
                    method: "post",
                    url: "/api/data_dump/fieldserver",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    data: $.param(JSON.parse($scope.models.fieldserver))
                }).success(function(data, status, headers, config) {
                    $scope.responses.fieldserver = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                }).error(function(data, status, headers, config) {
                    $scope.responses.fieldserver = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                });
            };

            $scope.submitInvensys = function() {
                $scope.responses.invensys = "Submitting...";
                $http({
                    method: "post",
                    url: "/api/data_dump/invensys",
                    headers: {"Content-Type": "multipart/form-data; boundary=----testboundary"},
                    data: "------testboundary\r\nContent-Disposition: form-data; name=\"file\"; filename=\"file\"\r\nContent-type: plain/text\r\n\r\n" + $scope.models.invensys + "\r\n------testboundary--\r\n",
                    transformRequest: angular.identity
                }).success(function(data, status, headers, config) {
                    $scope.responses.invensys = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                }).error(function(data, status, headers, config) {
                    $scope.responses.invensys = "Status: " + status + "\n" + JSON.stringify(data, undefined, 2);
                });
            };
        }
    ]);