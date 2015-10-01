angular.module("pathianApp.controllers")
    .controller("contractsNewCtrl", [
        "$scope", "$rootScope", "$location", "contractService",
        function ($scope, $rootScope, $location, contractService) {
            $rootScope.global.linkpath = "#/admin/contracts";

            $scope.showErrorMessage = false;
            $scope.model = {
                name: undefined,
                start_date: new Date(),
                end_date: new Date(),
                active: false,
                group: undefined,
                purchase_order_number: undefined,
                dollar_amount:  undefined,
                users: []
            };

            $scope.submit = function () {
                if ($scope.model.users) {
                    $scope.model.user_ids = $scope.model.users.map(function (contract) { if (contract.id) {return contract.id;} return contract;});
                }
                if($scope.model.group){
                    $scope.model.group_id = $scope.model.group.id;
                }
                contractService.save($scope.model, function () {
                    $location.path("/admin/contracts");
                }, function(e) {
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
                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                            name: { type: "string", validation: { required: true } }
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
