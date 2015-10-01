angular.module("pathianApp.controllers")
    .controller("utilitycompaniesNewCtrl", [
        "$scope", "$rootScope", "$location", "utilitycompanyService", "contactService",
        function ($scope, $rootScope, $location, utilitycompanyService, contactService) {
            $rootScope.global.linkpath = "#/admin/utilitycompanies";

            $scope.showErrorMessage = false;

            $scope.model = {
                contact: null
            };
            $scope.submit = function () {
                if ($scope.model.contact === null)
                    $scope.model.contact_id = "";
                else
                    $scope.model.contact_id = $scope.model.contact.id
                utilitycompanyService.save($scope.model, function () {
                    $location.path("/admin/utilitycompanies");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.contactGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Contacts",
                model: {
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        full_name:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field: "full_name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort: {field:"full_name", dir:"asc"}
            });

            $scope.cancel = function () {
                $location.path("/admin/utilitycompanies");
            }
        }
    ]);
