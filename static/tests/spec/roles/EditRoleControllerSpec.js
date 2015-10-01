"use strict";

describe('When adding new meetings', function () {
    var scope,
        controller,
        rootScope,
        location,
        routeParams,
        roleService;

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
        routeParams = {};
        roleService = {
            get: sinon.stub()
        };

        controller = $controller('rolesEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            $routeParams: routeParams,
            roleService: roleService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/roles').should.be.ok;
    });
});






