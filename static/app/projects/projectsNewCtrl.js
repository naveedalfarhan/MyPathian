angular.module("pathianApp.controllers")
    .controller("projectsNewCtrl", [
        "$scope", "$rootScope", "$location", "projectService",
        function($scope, $rootScope, $location, projectService) {
            $rootScope.global.linkpath = "#/commissioning/projects";

            $scope.model = {
                name:"",
                group_id: "",
                address: "",
                customer_project_id: "",
                architect_project_id: "",
                start_date: "",
                complete_date: "",
                estimated_cost: "",
                owner_id: "",
                comm_authority_id: "",
                engineer_id: ""
            };

            $scope.owner = null;
            $scope.comm_authority = null;
            $scope.engineer = null;

            $scope.showErrorMessage = false;

            $scope.submit = function() {
                if ($scope.owner)
                    $scope.model.owner_id = $scope.owner.id;
                if ($scope.comm_authority)
                    $scope.model.comm_authority_id = $scope.comm_authority.id;
                if ($scope.engineer)
                    $scope.model.engineer_id = $scope.engineer.id;
                projectService.save($scope.model, function(){
                    $location.path("/commissioning/projects");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.contactGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Contacts",
                model:{
                    id:"id",
                    fields:{
                        id: {type:"string"},
                        full_name:{type:"string"}
                    }
                },
                columns:[
                    {
                        title:"Name",
                        field:"full_name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"full_name", dir:"asc"}
            });

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format = 'MM/dd/yyyy';

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "groups",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name:{type:"string"}
                    }
                },
                columns: [
                    {
                        field:"name",
                        title:"Name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"name", dir:"asc"}
            })

            $scope.cancel = function () {
                $location.path("/commissioning/projects");
            }
        }
    ]);