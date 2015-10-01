"use strict";

describe('When adding editing an eco', function () {
    var scope,
        controller,
        rootScope,
        location,
        ecoService,
        routeParams;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        routeParams = {};
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
            save: sinon.stub(),
            get: sinon.stub()
        };

        controller = $controller('ecoEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            ecoService: ecoService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/commissioning/eco').should.be.ok;
    });

});
