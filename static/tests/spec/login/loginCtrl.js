/*
toBe: represents the exact equality (===) operator.
toEqual: represents the regular equality (==) operator.
toMatch: calls the RegExp match() method behind the scenes to compare string data.
toBeDefined: opposite of the JS "undefined" constant.
toBeUndefined: tests the actual against "undefined".
toBeNull: tests the actual against a null value - useful for certain functions that may return null, like those of regular expressions (same as toBe(null))
toBeTruthy: simulates JavaScript boolean casting.
toBeFalsy: like toBeTruthy, but tests against anything that evaluates to false, such as empty strings, zero, undefined, etc…
toContain: performs a search on an array for the actual value.
toBeLessThan/toBeGreaterThan: for numerical comparisons.
toBeCloseTo: for floating point comparisons.
toThrow: for catching expected exceptions.
*/


describe("Login controller", function() {
    var r = { };
    beforeEach(module("loginCtrl"));

    describe("with no logged in user", function() {

        beforeEach(inject(["$rootScope", "$controller", "$httpBackend",
            function($rootScope, $controller, $httpBackend) {
                r.$rootScope = $rootScope;
                r.$rootScope.global = {
                    user: null
                };
                r.$scope = $rootScope.$new();
                r.locationPathSpy = jasmine.createSpy("location.path()");

                r.$httpBackend = $httpBackend;

                r.loginCtrl = $controller("loginCtrl", {
                    $rootScope: r.$rootScope,
                    $scope: r.$scope,
                    $location: {
                        path: r.locationPathSpy
                    }
                });
            }
        ]));

        afterEach(function() {
            r.$httpBackend.verifyNoOutstandingExpectation();
            r.$httpBackend.verifyNoOutstandingRequest();
        });

        it("should display error message on unsuccessful login", function() {
            r.$httpBackend.expectPOST("/api/Login").respond(401, { Message: "This is the error message to display" });
            r.$scope.submitLogin();
            r.$httpBackend.flush();
            expect(r.$scope.showLoginError).toBe(true);
            expect(r.$scope.loginErrorMessage).toBe("This is the error message to display");
        });

        it("should redirect to home on successful login", function() {
            r.$httpBackend.expectPOST("/api/Login").respond(200, { });
            r.$scope.submitLogin();
            r.$httpBackend.flush();
            expect(r.$scope.showLoginError).toBe(false);
            expect(r.locationPathSpy).toHaveBeenCalledWith("/home");
        });
    });

    describe("with logged in user", function() {

        beforeEach(inject(["$rootScope", "$controller",
            function($rootScope, $controller) {
                r.$rootScope = $rootScope;
                r.$rootScope.global = {
                    user: {}
                };
                r.$scope = $rootScope.$new();
                r.locationPathSpy = jasmine.createSpy("location.path()");
                r.loginCtrl = $controller("loginCtrl", {
                    $rootScope: r.$rootScope,
                    $scope: r.$scope,
                    $location: {
                        path: r.locationPathSpy
                    }
                });
            }
        ]));

        it("should reroute to home", function() {
            expect(r.locationPathSpy).toHaveBeenCalledWith("/home");
        });
    });

});