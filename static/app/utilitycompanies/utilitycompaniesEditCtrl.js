angular.module("pathianApp.controllers")
    .controller("utilitycompaniesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "utilitycompanyService",
        function ($scope, $rootScope, $location, $routeParams, utilitycompanyService) {
            $rootScope.global.linkpath = "#/admin/utilitycompanies";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            utilitycompanyService.get({id:$scope.id}, function(model) {
                if (model.contact_id === null)
                    model.contact = null;
                else
                    model.contact = model.contact_model;

                $scope.model = model;
            });

            $scope.submit = function(){
                if ($scope.model.contact === null)
                    $scope.model.contact_id = "";
                else
                    $scope.model.contact_id = $scope.model.contact.id

                utilitycompanyService.update($scope.model, function(){
                    $location.path("/admin/utilitycompanies");
                }, function(e){
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
