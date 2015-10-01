angular.module("pathianApp.controllers")
    .controller("contractsEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "contractService",
        function ($scope, $rootScope, $location, $routeParams, contractService) {
            $rootScope.global.linkpath = "#/admin/contracts";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            contractService.get({id:$scope.id}, function(model) {
                $scope.model = model;
                $scope.model.users = model.users;
                $scope.model.group = model.group;

                if (model.start_date){
                    date = Date.parse(model.start_date);
                    $scope.model.start_date = new Date(date);
                }

                if (model.end_date){
                    date = Date.parse(model.end_date);
                    $scope.model.end_date = new Date(date);
                }
            });

            $scope.submit = function(){
                if ($scope.model.users) {
                    $scope.model.user_ids = $scope.model.users.map(function (contract) { if (contract.id) {return contract.id;} return contract;});
                }
                if($scope.model.group){
                    $scope.model.group_id = $scope.model.group.id;
                }
                contractService.update($scope.model, function(){
                    $location.path("/admin/contracts");
                }, function(e){
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.userGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Users",
                model: {
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        username:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Username",
                        field: "username"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort: {field:"username", dir:"asc"}
            });

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions(
                {
                    controllerName: "groups",
                    model: {
                        id: "id",
                        fields: {
                            Id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                            Name: { type: "string", validation: { required: true } }
                        }
                    },
                    columns: ["name"],
                    editable: false,
                    createTemplate: false,
                    defaultSort: { field: "name", dir: "asc" }
                });

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format='MM/dd/yyyy';

            $scope.cancel = function () {
                $location.path("/admin/contracts");
            };
        }
    ]);
