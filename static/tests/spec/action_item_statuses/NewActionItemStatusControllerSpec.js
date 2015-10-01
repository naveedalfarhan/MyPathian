"use strict";

describe('When adding new statuses', function () {
    var scope,
        controller,
        rootScope,
        location,
        actionItemStatusService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        actionItemStatusService = {
            save: sinon.stub()
        };

        controller = $controller('actionitemstatusesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            actionitemstatusService: actionItemStatusService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/actionitemstatuses').should.be.ok;
    });

});

