angular.module("pathianApp.controllers")
    .controller("bronzeReportingSummaryCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "$http", "$modal", "upload", "bronzeReportingFormService",
        function($scope, $rootScope, $location, $routeParams, $http, $modal, upload, formService){
            $rootScope.global.linkpath = "#/bronze/upload";
            $scope.model = formService.getData();
            $scope.postSuccess = false;


            if ($scope.model.gasAccount.enabled) {
                $scope.backLink = "#/bronze/upload/gas";
            } else {
                $scope.backLink = "#/bronze/upload/electric";
            }

            if ($scope.model.currentPage == 0)
                $location.path("/bronze/start");
            else if ($scope.model.currentPage == 1)
                $location.path("/bronze/upload");

            $scope.$on("$routeChangeStart", function() {
                var path = $location.path();
                if (path.substring(0, 7) != "/bronze")
                    formService.resetData();
            });



            $scope.submit = function() {
                var electricFile = $scope.model.electricAccount.enabled
                    && $scope.model.electricAccount.uploadFormat == "energyStar"
                    && $scope.model.electricAccount.energyStarData
                    && $scope.model.electricAccount.energyStarData[0];
                var gasFile = $scope.model.gasAccount.enabled
                    && $scope.model.gasAccount.uploadFormat == "energyStar"
                    && $scope.model.gasAccount.energyStarData
                    && $scope.model.gasAccount.energyStarData[0];


                $("#loadingSpinner").show();
                upload({
                    url: "/api/uploadBronzeReporting",
                    method: "post",
                    data: {
                        model: JSON.stringify($scope.model),
                        electricFile: electricFile,
                        gasFile: gasFile
                    }
                }).then(
                    function(res) {
                        $("#loadingSpinner").hide();
                        $scope.postSuccess = true;
                    },
                    function(res) {
                        $("#loadingSpinner").hide();
                        var modalWindow = $modal.open({
                            templateUrl: "submitErrorModal.html",
                            controller: ["$scope",
                                function($scope) {
                                    $scope.ok = function() {
                                        modalWindow.close();
                                    };
                                }
                            ]
                        });
                    }
                )
            };
        }
    ]);