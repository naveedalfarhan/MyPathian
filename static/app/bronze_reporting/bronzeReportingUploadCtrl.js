angular.module("pathianApp.controllers")
    .controller("bronzeReportingUploadCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "bronzeReportingFormService", "weatherstationService", "timezoneService",
        function($scope, $rootScope, $location, $routeParams, formService, weatherstationService, timezoneService){
            $rootScope.global.linkpath = "#/bronze/upload";
            $scope.model = formService.getData();
            $scope.accountType = $routeParams["accountType"];

            if ($scope.accountType == "electric") {
                $scope.units = [
                    {id: "kwh", name: "kWh (thousand Watt-hours)"},
                    {id: "mwh", name: "MWh (million Watt-hours)"},
                    {id: "kbtu", name: "kBtu (thousand Btu)"},
                    {id: "mmbtu", name: "MMBtu (million Btu)"},
                    {id: "gj", name: "GJ"}
                ]
            } else if ($scope.accountType == "gas") {
                $scope.units = [
                    {id: "mcf", name: "mcf (thousand cubic feet)"},
                    {id: "ccf", name: "ccf (hundred cubic feet)"},
                    {id: "cf", name: "cf (cubic feet)"},
                    {id: "cm", name: "Cubic meters"},
                    {id: "kbtu", name: "kBtu (thousand Btu)"},
                    {id: "mmbtu", name: "MMBtu (million Btu)"},
                    {id: "therms", name: "therms"},
                    {id: "gj", name: "GJ"}
                ]
            }

            if ($scope.accountType == "electric" && !$scope.model.electricAccount.enabled) {
                $location.path("/bronze/upload");
                return;
            } else if ($scope.accountType == "gas" && !$scope.model.gasAccount.enabled) {
                $location.path("/bronze/upload");
                return;
            }

            if ($scope.accountType == "electric" || !$scope.model.electricAccount.enabled)
                $scope.backLink = "#/bronze/upload";
            else
                $scope.backLink = "#/bronze/upload/electric";

            if ($scope.accountType == "electric")
                $scope.accountModel = $scope.model.electricAccount;
            else if ($scope.accountType == "gas")
                $scope.accountModel = $scope.model.gasAccount;



            $scope.weatherstations = weatherstationService.list(function() {
                $scope.accountModel.weatherstation_id = $scope.weatherstations[0].id;
            });
            $scope.timezones = timezoneService.query(function() {
                $scope.accountModel.timezone = $scope.timezones[0].name;
            });

            if ($scope.model.currentPage == 0)
                $location.path("/bronze/start");

            $scope.$on("$routeChangeStart", function() {
                var path = $location.path();
                if (path.substring(0, 7) != "/bronze")
                    formService.resetData();
            });

            $scope.next = function() {
                if ($scope.accountType == "gas" || !$scope.model.gasAccount.enabled) {
                    if ($scope.model.currentPage < 2)
                        $scope.model.currentPage = 2;
                    $location.path("/bronze/summary");
                } else
                    $location.path("/bronze/upload/gas");
            }
        }
    ]);