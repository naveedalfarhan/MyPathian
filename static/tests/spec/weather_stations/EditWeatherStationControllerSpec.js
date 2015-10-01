"use strict";

describe('When creating a new weather station', function () {
    var scope,
        controller,
        rootScope,
        location,
        routeParams,
        weatherstationService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        weatherstationService = {
            save: sinon.stub(),
            get: sinon.stub()
        };
        routeParams = {};
        location = {
            path: sinon.stub()
        };

        controller = $controller('weatherstationsEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            weatherstationService: weatherstationService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/weatherstations').should.be.ok;
    });

});



