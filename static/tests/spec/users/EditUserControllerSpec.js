"use strict";

describe('When editing an existing user', function () {
    var scope,
        controller,
        rootScope,
        location,
        routeParams,
        userService,
        roleService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        userService = {
            get: sinon.stub()
        };
        roleService = {};
        routeParams = {};
        location = {
            path: sinon.stub()
        };

        controller = $controller('usersEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            userService: userService,
            roleService: roleService
        });
    }));

    it('should go back to the list page when the user clicks the cancel button', function () {
        scope.cancel();

        location.path.calledWith('/admin/users').should.be.ok;
    });

});

