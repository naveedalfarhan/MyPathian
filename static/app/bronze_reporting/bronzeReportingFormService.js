angular.module("pathianApp.services")
    .factory("bronzeReportingFormService", function() {
        var _formData = {
            // page 0 is start, page 1 is upload, page 2 is summary
            currentPage: 0,
            electricAccount: {
                enabled: false,
                manualData: []
            },
            gasAccount: {
                enabled: false,
                manualData: []
            }
        };

        return {
            getData: function() {
                return _formData;
            },
            setData: function(newFormData) {
                _formData = newFormData;
            },
            resetData: function() {
                _formData = {
                    currentPage: 0
                };
            }
        }
    });