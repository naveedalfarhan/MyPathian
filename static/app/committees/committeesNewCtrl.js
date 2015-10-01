angular.module("pathianApp.controllers")
    .controller("committeesNewCtrl", [
        "$scope", "$rootScope", "$location", "committeeService",
        function($scope, $rootScope, $location, committeeService) {
            $rootScope.global.linkpath = "#/commissioning/committee";

            $scope.showErrorMessage = false;

            $scope.model = {
                name:"",
                facility_directors_ids:[],
                team_members_ids:[],
                corporate_energy_director_id:"",
                group_id:""
            };

            $scope.facilitydirectors = [];
            $scope.teammembers=[];

            $scope.submit = function() {
                $scope.model.facility_directors_ids = $scope.facilitydirectors.map(function (contact) { if (contact.id) {return contact.id;} return contact;});
                $scope.model.team_members_ids = $scope.teammembers.map(function (contact) { if (contact.id) {return contact.id;} return contact;});
                if ($scope.energydirector)
                    $scope.model.corporate_energy_director_id = $scope.energydirector.id;
                if ($scope.group)
                    $scope.model.group_id = $scope.group.id;
                committeeService.save($scope.model, function() {
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
            }
        }
    ]);