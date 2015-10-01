angular.module("pathianApp.services")
    .factory("resetScheduleService", [
        "$resource",
        function($resource) {
            return $resource("/api/ResetSchedules/:id",
                { id: "@id" },
                {
                    'update':{method:"PUT"},
                    'GetAll':{method:"GET"}
                }
            );
        }
    ]);

angular.module("pathianApp.services")
    .factory("resetScheduleData", [
        "$q",
        "resetScheduleService",
        function($q, resetScheduleService) {
            return function() {
                var promise = resetScheduleService.GetAll().$promise;

                return $q.when(promise).then(function(response) {
                    return response.results
                });
            };
        }
    ]);