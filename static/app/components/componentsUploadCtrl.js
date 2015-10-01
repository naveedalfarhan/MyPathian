angular.module("pathianApp.controllers")
    .controller("componentsUploadCtrl", ["$scope", "$rootScope", "$location", "$timeout", "componentUploadService",
        function ($scope, $rootScope, $location, $timeout, componentUploadService) {
            $rootScope.global.linkpath = "#/admin/components";

            $scope.state = "pick_file";
            $scope.upload_id = null;

            $scope.progressValue = 0;
            $scope.progressValueDisplay = "0%";
            $scope.progressType = "success";
            $scope.wetProgressValue = 0;
            $scope.wetProgressValueDisplay = "0%";
            $scope.wetProgressType = "success";

            $scope.results = null;

            $scope.showSkipped = false;
            $scope.showNameChanged = false;
            $scope.showAdded = false;
            $scope.showErrors = true;


            $scope.uploadAsyncProps = {
                saveUrl: '/api/uploadDryComponents',
                autoUpload: false
            };

            $scope.uploadSuccess = function(e) {
                var return_obj = JSON.parse(e.XMLHttpRequest.responseText);
                $scope.upload_id = return_obj["upload_id"];
                $scope.state = "dry_progress";
                $scope.$apply();
                $scope.startDryUpload();
            };

            var uploadTimerPromise = null;

            $scope.startDryUpload = function() {
                if (uploadTimerPromise) {
                    $timeout.cancel(uploadTimerPromise);
                    uploadTimerPromise = null;
                }

                (function tick() {
                    componentUploadService.uploadDryComponentsProgress({upload_id: $scope.upload_id}, {}, function(result) {
                        if (result.finished) {
                            if (!result.error) {
                                $scope.progressValue = 100;
                                $scope.progressValueDisplay = "100%";
                                $scope.progressType = "success";

                                $scope.state = "dry_progress_loading_results";
                                componentUploadService.uploadDryComponentsResults({upload_id: $scope.upload_id}, {}, function(results) {
                                    $scope.results = results;
                                    $scope.state = "dry_results";
                                });
                            } else {
                                $scope.progressValue = 100;
                                $scope.progressValueDisplay = "Error!";
                                $scope.progressType = "danger";
                            }
                        }else {
                            $scope.progressValue = parseInt(result.current_progress_point / result.total_progress_points * 100.0);
                            $scope.progressValueDisplay = $scope.progressValue + "%";
                            $scope.progressType = "success";
                            uploadTimerPromise = $timeout(tick, 1000);
                        }
                    }, function() {
                        $scope.progressValue = 100;
                        $scope.progressValueDisplay = "Error!";
                        $scope.progressType = "danger";
                    });
                })();
            };

            $scope.startWetUpload = function() {
                if (uploadTimerPromise) {
                    $timeout.cancel(uploadTimerPromise);
                    uploadTimerPromise = null;
                }

                (function tick() {
                    componentUploadService.uploadComponentsProgress({upload_id: $scope.upload_id}, {}, function(result) {
                        $scope.progress = result;
                        if (result.finished) {
                            if (!result.error) {
                                $scope.wetProgressValue = 100;
                                $scope.wetProgressValueDisplay = "100%";
                                $scope.wetProgressType = "success";
                                $scope.state = "wet_finished";
                            } else {
                                $scope.wetProgressValue = 100;
                                $scope.wetProgressValueDisplay = "Error!";
                                $scope.wetProgressType = "danger";
                            }
                        }else {
                            $scope.wetProgressValue = parseInt(result.current_progress_point / result.total_progress_points * 100.0);
                            $scope.wetProgressValueDisplay = $scope.wetProgressValue + "%";
                            $scope.wetProgressType = "success";
                            uploadTimerPromise = $timeout(tick, 1000);
                        }
                    }, function() {
                        $scope.wetProgressValue = 100;
                        $scope.wetProgressValueDisplay = "Error!";
                        $scope.wetProgressType = "danger";
                    });
                })();
            };

            $scope.cancel = function() {
                $scope.upload_id = null;
                $scope.results = null;
                $scope.state = "pick_file";
            };

            $scope.submit = function() {
                $scope.state = "wet_progress";
                componentUploadService.uploadComponents({upload_id: $scope.upload_id}, {}, $scope.startWetUpload);
            };

            $scope.showRow = function(r) {
                if (r.exists) {
                    if (!r.action && !r.error)
                        return $scope.showSkipped;
                    else if (r.action && !r.error)
                        return $scope.showNameChanged;
                } else {
                    if (!r.error && r.action)
                        return $scope.showAdded;
                    else if (r.error && r.action)
                        return $scope.showErrors;
                }
            };
        }
    ]);