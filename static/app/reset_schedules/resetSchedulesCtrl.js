angular.module("pathianApp.controllers")
    .controller("resetSchedulesCtrl", ["$scope", "$rootScope", "$routeParams", "$location", "$http", "$modal", "$compile", "resetScheduleService", "initialData", "toaster",
        function($scope, $rootScope, $routeParams, $location, $http, $modal, $compile, resetScheduleService, initialData, toaster) {
            $rootScope.global.linkpath = '#/admin/resetschedules';

            $scope.resetSchedules = initialData;

            function newSubmit(resetSchedule) {
                kendo.ui.progress($(".pat-container"), true);
                var test = resetScheduleService.save(resetSchedule, function(response) {
                    resetSchedule.id = response.id;
                    $scope.resetSchedules.push(resetSchedule);

                    toaster.pop('success', "Success", "Reset Schedule Saved");
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", "An Error Occurred")
                }).$promise.finally(function(){
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function editSubmit(resetSchedule) {
                kendo.ui.progress($(".pat-container"), true);
                resetScheduleService.update(resetSchedule, function(response) {
                    var resetScheduleInList = _.find($scope.resetSchedules, function(item) {
                        return resetSchedule.id === item.id;
                    });

                    var index = _.indexOf($scope.resetSchedules, resetScheduleInList);

                    if (index > -1) {
                        $scope.resetSchedules[index].name = resetSchedule.name;
                        $scope.resetSchedules[index].header1 = resetSchedule.header1;
                        $scope.resetSchedules[index].header2 = resetSchedule.header2;
                        $scope.resetSchedules[index].row1val1 = resetSchedule.row1val1;
                        $scope.resetSchedules[index].row1val2 = resetSchedule.row1val2;
                        $scope.resetSchedules[index].row2val1 = resetSchedule.row2val1;
                        $scope.resetSchedules[index].row2val2 = resetSchedule.row2val2;
                    }

                    toaster.pop('success', "Success", "Reset Schedule Saved");
                }, function(httpResponse) {
                    toaster.pop('error', "Edit Failed", "An Error Occurred")
                }).$promise.finally(function(){
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function deleteSubmit(resetSchedule) {
                kendo.ui.progress($(".pat-container"), true);
                resetScheduleService.delete(resetSchedule, function(response) {
                    var index = _.indexOf($scope.resetSchedules, resetSchedule);

                    if (index > -1) {
                        $scope.resetSchedules.splice(index, 1);
                    }

                    toaster.pop('success', "Success", "Reset Schedule Deleted");
                }, function(httpResponse) {
                    toaster.pop('error', "Delete Failed", "An Error Occurred")
                }).$promise.finally(function(){
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            $scope.newResetSchedule = function() {
                var modalInstance = $modal.open({
                    templateUrl: 'resetScheduleModal',
                    controller: ResetScheduleModalCtrl,
                    resolve: {data: function(){return undefined;}}
                });

                modalInstance.result.then(function (result) {
                    newSubmit(result);
                });
            };

            $scope.editResetSchedule = function(resetSchedule) {
                var modalInstance = $modal.open({
                    templateUrl: 'resetScheduleModal',
                    controller: ResetScheduleModalCtrl,
                    resolve: {
                        data: function(){return _.clone(resetSchedule);}
                    }
                });

                modalInstance.result.then(function (result) {
                    result.id = resetSchedule.id;
                    editSubmit(result);
                });
            };

            $scope.deleteResetSchedule = function(resetSchedule) {
                deleteSubmit(resetSchedule);
            };
        }
    ]);

var ResetScheduleModalCtrl = function ($scope, $modalInstance, data) {
    $scope.data = data || {name:'', header1: '', header2: '', row1val1: '', row1val2: '', row2val1: '', row2val2: ''};
  
    $scope.ok = function () {
        $modalInstance.close($scope.data);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
};