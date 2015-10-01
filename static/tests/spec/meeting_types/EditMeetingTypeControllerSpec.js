"use strict";

describe('When adding editing meeting types', function () {
    var scope,
        controller,
        rootScope,
        location,
        routeParams,
        meetingtypeService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        location = {
            path: sinon.stub()
        };
        meetingtypeService = {
            save: sinon.stub(),
            get: sinon.stub()
        };
        routeParams = {};

        controller = $controller('meetingtypesEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            meetingtypeService: meetingtypeService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith("/admin/meetingtypes").should.be.ok;
    });
});



