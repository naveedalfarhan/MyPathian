angular.module("pathianApp.controllers")
    .controller("ecoNewCtrl", [
        "$scope", "$rootScope", "$location", "ecoService",
        function($scope, $rootScope, $location, ecoService) {
            $rootScope.global.linkpath = "#/commissioning/eco";

            $scope.showErrorMessage = false;

            $scope.model = {
                original_date: new Date(),
                completion_goal: new Date()
            };

            $scope.submit = function(){
                if ($scope.project)
                    $scope.model.project_id = $scope.project.id;
                ecoService.save($scope.model, function(){
                    $location.path("/commissioning/eco");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.equipment = [];

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format = 'MM/dd/yyyy';

            $scope.projectGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Projects",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field:"name"
                    }
                ],
                editable: false,
                createTemplate: false,
                defaultSort: {field:"name", dir:"asc"}
            });

            $scope.cancel = function () {
                $location.path("/commissioning/eco");
            }
        }
    ]);