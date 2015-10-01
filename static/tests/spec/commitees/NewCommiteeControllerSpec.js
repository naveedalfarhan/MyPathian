"use strict";

describe('When adding new commitees', function () {
    var scope,
        controller,
        rootScope,
        location,
        committeeService;

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
        committeeService = {
            save: sinon.stub()
        };

        controller = $controller('committeesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            committeeService: committeeService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith("/commissioning/committees").should.be.ok;
    });
});


