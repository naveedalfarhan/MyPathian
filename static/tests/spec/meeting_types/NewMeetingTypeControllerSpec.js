"use strict";

describe('When adding new meeting types', function () {
    var scope,
        controller,
        rootScope,
        location,
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
            save: sinon.stub()
        };

        controller = $controller('meetingtypesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            meetingtypeService: meetingtypeService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith("/admin/meetingtypes").should.be.ok;
    });
});



