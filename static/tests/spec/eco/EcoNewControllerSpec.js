"use strict";

describe('When adding new eco', function () {
    var scope,
        controller,
        rootScope,
        location,
        ecoService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: function () {

                }
            }
        };
        location = {
            path: sinon.stub()
        };
        ecoService = {
            save: sinon.stub()
        };

        controller = $controller('ecoNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            ecoService: ecoService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/commissioning/eco').should.be.ok;
    });

});



