angular.module('pathianApp.interceptor', ['ngResource'])
    .factory('httpResponseInterceptor', ['$q', '$location',
        function($q, $location) {
            return {
                response: function(response) {
                    if (response.status === 403) {
                        $location.path('/forbidden').search('returnTo', $location.path());
                    }
                    // return the response to the original callback function
                    return response || $q.when(response);
                },
                responseError: function(rejection) {
                    if (rejection.status === 403) {
                        $location.path('/forbidden').search('returnTo', $location.path());
                    }
                    // return the response to the original callback function, but mark it as rejected
                    return $q.reject(rejection);
                }
            }
        }
    ])
    .config(['$httpProvider', function($httpProvider) {
        $httpProvider.interceptors.push('httpResponseInterceptor');
    }]);