"use strict";

describe('when entering an action item priority', function () {
    var scope,
        controller,
        rootScope,
        location,
        actionItemPriorityService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        actionItemPriorityService = {
            save: sinon.stub()
        };

        controller = $controller('actionitemprioritiesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            actionitempriorityService: actionItemPriorityService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/actionitempriorities').should.be.ok;
    });
});

describe("when editing an action item priority", function () {
    var scope,
        controller,
        rootScope,
        location,
        actionItemPriorityService,
        routeParams;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        actionItemPriorityService = {
            save: sinon.stub(),
            get: sinon.stub()
        };
        routeParams = {};

        controller = $controller('actionitemprioritiesEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            actionitempriorityService: actionItemPriorityService
        });
    }));

    it("should go back to the list page when the user hits cancel", function () {
        scope.cancel();

        location.path.calledWith('/admin/actionitempriorities').should.be.ok;
    });
});
