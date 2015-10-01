"use strict";

describe('When adding new group', function () {
    var scope,
        controller,
        rootScope,
        location,
        groupService,
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
        groupService = {};
        weatherstationService = {
            list: sinon.stub()
        };
        naicsService = {
            getLevelFive: sinon.stub()
        };
        sicService = {
            getLevelTwo: sinon.stub()
        };

        controller = $controller('groupsNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
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




