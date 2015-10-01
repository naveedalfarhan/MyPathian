angular.module("pathianApp.controllers")
    .controller("loginCtrl", ["$scope", "$rootScope", "$http", "$location", "permissionsFactory",
        function ($scope, $rootScope, $http, $location, permissionsFactory) {
            if ($rootScope.global.user !== null) {
                $location.path("/home");
                return;
            }
            $rootScope.global.linkpath = "#/login";
            
            $scope.showLoginError = false;
            
            $scope.submitLogin = function () {
                $scope.showLoginError = false;
                var postData = {
                    username: $scope.username,
                    password: $scope.password,
                    rememberMe: $scope.rememberMe
                };
                $http.post("/api/Login", postData)
                    .then(function (response) {
                        console.log(response);
                        $rootScope.global.user = response.data;
                        $rootScope.global.reportingGroup = response.data.reporting_group;
                        permissionsFactory.setPermissions(response.data.permissions);
                        $rootScope.global.updatePermissions();
                        $location.path("/home");
                    }, function (response) {
                        console.log(response);
                        $scope.loginErrorMessage = response.data.Message;
                        $scope.showLoginError = true;
                    });
            };
        }
    ]);