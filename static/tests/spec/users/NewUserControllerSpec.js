"use strict";

describe('When creating a new user', function () {
    var scope,
        controller,
        rootScope,
        location,
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
        userService = {};
        roleService = {};
        location = {
            path: sinon.stub()
        };

        controller = $controller('usersNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            userService: userService,
            roleService: roleService
        });
    }));

    it('should go back to the list page when the user clicks the cancel button', function () {
        // TODO: Complete this test when review of the user page comes up
        scope.cancel();

        location.path.calledWith('/admin/users').should.be.ok;
    });

});
