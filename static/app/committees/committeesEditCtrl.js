angular.module("pathianApp.controllers")
    .controller("committeesEditCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "committeeService",
        function($scope, $rootScope, $routeParams, $location, committeeService) {
            $rootScope.global.linkpath = "#/commissioning/committees";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            $scope.model = committeeService.get({id:$scope.id}, function(model) {
                $scope.model = model;

                $scope.energydirector = model.energy_director_model;
                $scope.facilitydirectors = model.facility_directors_model;
                $scope.teammembers = model.team_members_model;
                $scope.group = model.group_model;

            });

            $scope.submit = function() {
                $scope.model.facility_directors_ids = $scope.facilitydirectors.map(function (contact) { if (contact.id) {return contact.id;} return contact;});
                $scope.model.team_members_ids = $scope.teammembers.map(function (contact) { if (contact.id) {return contact.id;} return contact;});
                $scope.model.corporate_energy_director_id = $scope.energydirector.id;
                $scope.model.group_id = $scope.group.id;
                committeeService.update($scope.model, function() {
                    $location.path("/commissioning/committees");
                }, function(e) {
                    $scope.showErrorMessage = true;
                    $scope.message = e.data.message;
                })
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

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName:"groups",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name: {type:"string"}
                    }
                },
                columns:[
                    {
                        field:"name",
                        title:"Name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"name", dir:"asc"}
            });

            $scope.cancel = function () {
                $location.path("/commissioning/committees");
            };
        }
    ]);