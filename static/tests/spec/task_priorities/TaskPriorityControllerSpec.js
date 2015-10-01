"use strict";

describe('When adding new priority tasks', function () {
    var scope,
        controller,
        rootScope,
        location,
        taskPriorityService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        taskPriorityService = {
            save: sinon.stub()
        };

        controller = $controller('taskprioritiesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            taskPriorityService: taskPriorityService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/taskpriorities').should.be.ok;
    });

});



