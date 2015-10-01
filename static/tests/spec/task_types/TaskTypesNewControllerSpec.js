"use strict";

describe('When adding new task types', function () {
    var scope,
        controller,
        rootScope,
        location,
        taskTypeService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        taskTypeService = {
            save: sinon.stub()
        };

        controller = $controller('tasktypesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            taskTypeService: taskTypeService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/tasktypes').should.be.ok;
    });

});

