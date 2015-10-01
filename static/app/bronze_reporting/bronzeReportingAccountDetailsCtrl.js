angular.module("pathianApp.controllers")
    .controller("bronzeReportingAccountDetailsCtrl", [
        "$scope", "$rootScope", "$location", "$modal", "bronzeReportingFormService",
        function($scope, $rootScope, $location, $modal, formService){
            $rootScope.global.linkpath = "#/bronze/upload";
            $scope.model = formService.getData();

            if ($scope.model.currentPage == 0)
                $location.path("/bronze/start");
            if ($scope.model.currentPage == 1)
                $location.path("/bronze/upload");

            $scope.model.electricAccount.name = $scope.model.name + " Electric";
            $scope.model.gasAccount.name = $scope.model.name + " Gas";


            $scope.next = function() {
                if (!$scope.model.electricAccount.enabled && !$scope.model.gasAccount.enabled) {
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
                } else if ($scope.model.electricAccount.enabled) {
                    $location.path("/bronze/upload/electric");
                } else if ($scope.model.gasAccount.enabled) {
                    $location.path("/bronze/upload/gas");
                }
            };


            $scope.$on("$routeChangeStart", function() {
                var path = $location.path();
                if (path.substring(0, 7) != "/bronze")
                    formService.resetData();
            });
        }
    ]);