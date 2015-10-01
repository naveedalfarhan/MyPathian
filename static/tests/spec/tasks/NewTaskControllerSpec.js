"use strict";

describe('When adding new task types', function () {
    var scope,
        controller,
        rootScope,
        location,
        taskTypeService,
        taskService,
        equipmentService,
        taskStatusService,
        taskPriorityService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        scope.global = {
            user: { primary_group: { id: '' } }
        };
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        location = {
            path: sinon.stub()
        };
        taskTypeService = {
            GetAll: sinon.stub()
        };
        taskService = {};
        equipmentService = {
            getAllForGroup: sinon.stub()
        };
        taskStatusService = {
            GetAll: sinon.stub()
        };
        taskPriorityService = {
            GetAll: sinon.stub()
        };

        controller = $controller('tasksNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            taskTypeService: taskTypeService,
            taskService: taskService,
            equipmentService: equipmentService,
            taskStatusService: taskStatusService,
            taskPriorityService: taskPriorityService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/commissioning/tasks').should.be.ok;
    });
});


