angular.module("pathianApp.controllers")
    .controller("bronzeReportingSubmissionsListCtrl", ["$scope", "$rootScope", "bronzeSubmissionService",
        function ($scope, $rootScope, bronzeSubmissionService) {
            $rootScope.global.linkpath = "#/admin/bronzeSubmissions";
            
            $scope.submissions = bronzeSubmissionService.query();

            $scope.process = function(submission) {
                new_submission = bronzeSubmissionService.process({"id": submission["id"]}, function() {
                    submission["processing_state"] = new_submission["processing_state"];
                });
            }
        }
    ]);