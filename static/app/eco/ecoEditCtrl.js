angular.module("pathianApp.controllers")
    .controller("ecoEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "ecoService",
        function($scope, $rootScope, $location, $routeParams, ecoService) {
            $rootScope.global.linkpath = "#/commissioning/eco";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            $scope.model = {};

            ecoService.get({id:$scope.id}, function(model) {
                $scope.model = model;

                var date = Date.parse(model.original_date);
                $scope.model.original_date = new Date(date);

                date = Date.parse(model.completion_goal);
                $scope.model.completion_goal = new Date(date);

                $scope.project = model.project_model;
            });

            $scope.submit = function() {
                if ($scope.project)
                    $scope.model.project_id = $scope.project.id;
                ecoService.update($scope.model, function() {
                    $location.path("/commissioning/eco");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

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