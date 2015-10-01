angular.module("pathianApp.controllers")
    .controller("notificationsCtrl", ["$scope", "$rootScope", "userService",
        function($scope, $rootScope, userService) {
            $rootScope.global.linkpath = "#/home/notifications";


            $scope.user_id = $rootScope.global.user.UserId;

            $scope.removeNotification = function(notificationId){
                userService.deleteNotification({'id':$scope.user_id, 'notificationId':notificationId}, function(data){

                });
            };
        }
    ]);