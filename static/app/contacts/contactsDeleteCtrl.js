angular.module("pathianApp.controllers")
    .controller("contactsDeleteCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "contactService",
        function ($scope, $rootScope, $location, $routeParams, contactService) {
            $rootScope.global.linkpath = "#/commissioning/contacts";

            $scope.showErrorMessage = false;

            $scope.id = $routeParams.id;

            contactService.get({ id: $scope.id }, function(model){
                $scope.model = model;
                $scope.fullname = model.first_name + " " + model.last_name
            });

            $scope.cancel = function(){
                $location.path("/commissioning/contacts")
            };

            $scope.submit = function (){
                var model = {
                    id: $scope.id
                };
                contactService["delete"](model, function(){
                   $location.path("/commissioning/contacts");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scop.showErrorMessage = true;
                });
            };
        }
    ]);