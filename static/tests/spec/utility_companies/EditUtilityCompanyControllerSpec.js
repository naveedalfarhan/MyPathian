"use strict";

describe('When editing a utility company', function () {
    var scope,
        controller,
        rootScope,
        location,
        routeParams,
        utilitycompanyService;


    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        utilitycompanyService = {
            get: sinon.stub()
        };

        location = {
            path: sinon.stub()
        };
        routeParams = {};

        controller = $controller('utilitycompaniesEditCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            utilitycompanyService: utilitycompanyService,
            $routeParams: routeParams
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/utilitycompanies').should.be.ok;
    });

});


