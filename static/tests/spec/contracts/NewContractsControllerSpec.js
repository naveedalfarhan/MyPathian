"use strict";

describe('When adding new commitees', function () {
    var scope,
        controller,
        rootScope,
        location,
        contractService;

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
        contractService = {
            save: sinon.stub()
        };

        controller = $controller('contractsNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            contractService: contractService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith("/admin/contracts").should.be.ok;
    });
});



