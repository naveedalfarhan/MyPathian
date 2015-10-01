"use strict";

describe('When adding new types', function () {
    var scope,
        controller,
        rootScope,
        location,
        actionitemtypeService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {}
        };
        location = {
            path: sinon.stub()
        };
        actionitemtypeService = {
            save: sinon.stub()
        };

        controller = $controller('actionitemtypesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            actionitemtypeService: actionitemtypeService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/actionitemtypes').should.be.ok;
    });

});


