"use strict";

describe('When adding syrx category', function () {
    var scope,
        controller,
        rootScope,
        location,
        syrxCategoryService;

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

        syrxCategoryService = {};

        controller = $controller('syrxCategoriesNewCtrl', {
            $scope: scope,
            $rootScope: rootScope,
            $location: location,
            syrxCategoryService: syrxCategoryService
        });
    }));

    it('should take the user back to the list page when they cancel', function () {
        scope.cancel();

        location.path.calledWith('/admin/syrxcategories').should.be.ok;
    });
});





