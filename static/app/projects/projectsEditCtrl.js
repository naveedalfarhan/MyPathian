angular.module("pathianApp.controllers")
    .controller("projectsEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "projectService",
        function($scope, $rootScope, $location, $routeParams, projectService) {
            $rootScope.global.linkpath = "#/commissioning/projects";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            $scope.model = projectService.get({id:$scope.id}, function(model) {
                $scope.model = model;

                $scope.owner = model.owner_model;
                $scope.comm_authority = model.comm_authority_model;
                $scope.engineer = model.engineer_model;

                var date = Date.parse(model.start_date);
                $scope.model.start_date = new Date(date);

                date = Date.parse(model.complete_date);
                $scope.model.complete_date = new Date(date);
            });

            $scope.submit = function() {
                if ($scope.owner)
                    $scope.model.owner_id = $scope.owner.id;
                if ($scope.comm_authority)
                    $scope.model.comm_authority_id = $scope.comm_authority.id;
                if ($scope.engineer)
                    $scope.model.engineer_id = $scope.engineer.id;
                projectService.update($scope.model, function() {
                    $location.path("/commissioning/projects");
                }, function(e) {
                    $scope.showErrorMessage = true;
                    $scope.message = e.data.message;
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
            });
        }
    ]);