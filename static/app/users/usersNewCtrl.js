angular.module("pathianApp.controllers")
    .controller("usersNewCtrl", [
        "$scope", "$rootScope", "$location", "userService", "roleService",
        function($scope, $rootScope, $location, userService, roleService) {
            $rootScope.global.linkpath = "#/admin/users";

            $scope.message = "";

            $scope.model = {
                username:undefined,
                roles:[],
                primary_group:undefined,
                groups:[],
                password:undefined,
                active: true,
                expiration_date: new Date(),
                email:undefined,
                address:undefined,
                city:undefined,
                state:undefined,
                zip:undefined,
                first_name: undefined,
                last_name: undefined,
                job_title: undefined
            };

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };
            $scope.format = 'MM/dd/yyyy';

            $scope.submit = function() {
                var user = {
                    username: $scope.model.username,
                    roles: $scope.model.roles.map(function(entry){return entry.id}),
                    primary_group_id: $scope.model.primary_group.id,
                    group_ids: $scope.model.groups.map(function(entry){return entry.id}),
                    password: $scope.model.password,
                    active: $scope.model.active,
                    expiration_date: $scope.model.expiration_date,
                    email: $scope.model.email,
                    address: $scope.model.address,
                    city: $scope.model.city,
                    state: $scope.model.state,
                    zip: $scope.model.zip,
                    first_name: $scope.model.first_name,
                    last_name: $scope.model.last_name,
                    job_title: $scope.model.job_title
                };
                console.log(user);
                userService.save(user, function() {
                    $location.path("/admin/users");
                }, function(e){
                    if (e.status == 401){
                        $location.path("/login");
                    }
                    $scope.message = e.data.message;
                });
            };
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

            $scope.roleGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Roles",
                model: {
                    id: "id",
                    fields: {
                        id: { type: "string", editable: false },
                        name: { type: "string", editable: false}
                    }
                },
                columns:["name"],
                editable: false,
                createTemplate: false,
                defaultSort: { field: "name", dir: "asc" }
            });

            $scope.cancel = function () {
                $location.path("/admin/users");
            };
        }
    ]);