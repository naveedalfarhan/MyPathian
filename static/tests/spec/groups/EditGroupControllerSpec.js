"use strict";

describe('When adding new group', function () {
    var scope,
        controller,
        rootScope,
        location,
        groupService,
        routeParams,
        weatherstationService,
        naicsService,
        sicService;

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
        groupService = {
            get: sinon.stub()
        };
        weatherstationService = {
            list: sinon.stub()
        };
        naicsService = {
            getLevelFive: sinon.stub()
        };
        sicService = {
            getLevelTwo: sinon.stub()
        };
        routeParams = {};

        controller = $controller('groupsEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            groupService: groupService,
            weatherstationService: weatherstationService,
            naicsService: naicsService,
            sicService: sicService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/groups').should.be.ok;
    });

});





