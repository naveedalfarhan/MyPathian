"use strict";

describe('When adding new meetings', function () {
    var scope,
        controller,
        rootScope,
        location,
        meetingService,
        meetingTypeService,
        projectService;

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
        meetingTypeService = {
            getAll: sinon.stub()
        };
        projectService = {
            GetAll: sinon.stub()
        };
        meetingService = {};

        controller = $controller('meetingsNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            meetingService: meetingService,
            meetingtypeService: meetingTypeService,
            projectService: projectService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/commissioning/meetings').should.be.ok;
    });
});




