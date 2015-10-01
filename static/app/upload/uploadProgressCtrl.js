angular.module("pathianApp.controllers")
    .controller("uploadProgressCtrl", [
        "$scope", "$rootScope", "$location", "$interval", "uploadProgressService",
        function ($scope, $rootScope, $location, $interval, uploadProgressService) {
            $rootScope.global.linkpath = "#/reporting/uploadProgress";

            $scope.uploads = [];

            var uploadsById = {};
            var timer = $interval(function() {
                var uploads = uploadProgressService.query(function() {
                    var existingUploads = {};
                    for (var i = 0; i < uploads.length; ++i) {
                        existingUploads[uploads[i]["id"]] = uploads[i];
                        if (!(uploads[i]["id"] in uploadsById)) {
                            uploadsById[uploads[i]["id"]] = uploads[i];
                            var cp = parseFloat(uploads[i]["current_progress_point"]);
                            var tp = parseFloat(uploads[i]["total_progress_points"]);
                            uploads[i]["percent"] =  Math.round(cp / tp * 100);
                            uploads[i]["progressMessage"] = uploads[i]["percent"] + "%";
                            uploads[i]["progressType"] = "success";
                            if (uploads[i]["error"]) {
                                uploads[i]["percent"] = 100;
                                uploads[i]["progressMessage"] = "Error!";
                                uploads[i]["progressType"] = "danger";
                            }
                            $scope.uploads.push(uploads[i]);
                        } else {
                            var newUpload = uploads[i];
                            var oldUpload = uploadsById[newUpload["id"]];

                            var updateCP = newUpload["current_progress_point"] != oldUpload["current_progress_point"];
                            var updateTP = newUpload["total_progress_points"] != oldUpload["total_progress_points"];
                            var updateComplete = newUpload["complete"] != oldUpload["complete"];
                            var updateError = newUpload["error"] != oldUpload["error"];
                            var updateMessage = newUpload["message"] != oldUpload["message"];

                            if (updateCP)
                                oldUpload["current_progress_point"] = parseFloat(newUpload["current_progress_point"]);
                            if (updateTP)
                                oldUpload["total_progress_points"] = parseFloat(newUpload["total_progress_points"]);
                            if (updateCP || updateTP) {
                                oldUpload["percent"] =  Math.round(oldUpload["current_progress_point"] / oldUpload["total_progress_points"] * 100);
                                oldUpload["progressMessage"] = oldUpload["percent"] + "%";
                                oldUpload["progressType"] = "success";
                            }
                            if (updateComplete)
                                oldUpload["complete"] = newUpload["complete"];
                            if (updateError) {
                                oldUpload["error"] = newUpload["error"];
                                if (oldUpload["error"]) {
                                    uploads[i]["percent"] = 100;
                                    oldUpload["progressMessage"] = "Error!";
                                    oldUpload["progressType"] = "danger";
                                }
                            }
                            if (updateMessage)
                                oldUpload["message"] = newUpload["message"];
                        }
                    }
                    for (var i = $scope.uploads.length - 1; i >= 0; --i)
                        if (!($scope.uploads[i]["id"] in existingUploads))
                            $scope.uploads.splice(i, 1);
                });
            }, 1000, 0, true);

            $scope.$on("$destroy", function() {
                if (timer)
                    $interval.cancel(timer);
            });
        }
    ]);