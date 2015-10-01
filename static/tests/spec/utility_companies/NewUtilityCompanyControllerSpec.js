"use strict";

describe('When creating a new user', function () {
    var scope,
        controller,
        rootScope,
        location,
        utilitycompanyService,
        contactService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        utilitycompanyService = {};

        location = {
            path: sinon.stub()
        };
        contactService = {};

        controller = $controller('utilitycompaniesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            utilitycompanyService: utilitycompanyService,
            contactService: contactService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/utilitycompanies').should.be.ok;
    });

});

