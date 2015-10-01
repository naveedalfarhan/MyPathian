angular.module("pathianApp.controllers")
    .controller("bronzeReportingStartCtrl", [
        "$scope", "$rootScope", "$location", "bronzeReportingFormService", "naicsService", "sicService",
        function($scope, $rootScope, $location, formService, naicsService, sicService){
            $rootScope.global.linkpath = "#/bronze/start";
            $scope.model = formService.getData();

            $scope.naicsCodes = naicsService.getLevelFive(function() {
                $scope.model.naics = $scope.naicsCodes[0].code;
            });
            $scope.sicCodes = sicService.getLevelTwo(function() {
                $scope.model.sic = $scope.sicCodes[0].code;
            });

            $scope.next = function() {
                if ($scope.model.currentPage < 1)
                    $scope.model.currentPage = 1;
                $location.path("/bronze/upload");
            };

            $scope.$on("$routeChangeStart", function() {
                var path = $location.path();
                if (path.substring(0, 7) != "/bronze")
                    formService.resetData();
            });
        }
    ]);