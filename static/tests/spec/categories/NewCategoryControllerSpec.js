"use strict";

describe('When adding new category', function () {
    var scope,
        controller,
        rootScope,
        location,
        categoryService;

    beforeEach(module("pathianApp.controllers"));
    beforeEach(inject(function ($rootScope, $controller) {
        scope = $rootScope.$new();
        rootScope = {
            global: {
                getJsonGridOptions: sinon.stub()
            }
        };
        location = {
            path: sinon.stub()
        };
        categoryService = {};

        controller = $controller('categoriesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            categoryService: categoryService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith("/commissioning/categories").should.be.ok;
    });
});



