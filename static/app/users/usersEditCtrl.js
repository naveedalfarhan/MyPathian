angular.module("pathianApp.controllers")
    .controller("usersEditCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "userService", "roleService",
        function($scope, $rootScope, $routeParams, $location, userService, roleService) {
            $rootScope.global.linkpath = "#/admin/users";
            $scope.id = $routeParams.id;

            $scope.message = "";

            $scope.model = {
                username:undefined,
                roles:[],
                primary_group:undefined,
                groups:[],
                password:undefined,
                active: true,
                expiration_date:new Date(),
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

            userService.get({ id: $scope.id }, function(user) {
                $scope.model.username = user.username;
                $scope.model.roles = user.roles;
                $scope.model.primary_group = user.primary_group;
                $scope.model.groups = user.groups;
                $scope.model.active = user.active;
                $scope.model.email = user.email;
                $scope.model.address = user.address;
                $scope.model.city = user.city;
                $scope.model.state = user.state;
                $scope.model.zip = user.zip;
                $scope.model.first_name = user.first_name;
                $scope.model.last_name = user.last_name;
                $scope.model.job_title = user.job_title;
                if (user.expiration_date) {
                    var exp = Date.parse(user.expiration_date);
                    $scope.model.expiration_date = new Date(exp);
                }
            },function(data){
                switch (data.status){
                    case 401:
                        $location.path("/login")
                }
            });

            $scope.submit = function() {
                if ($scope.model.primary_group == undefined) {
                    $scope.message = "Primary group is required.";
                } else {
                    var user = {
                        id: $scope.id,
                        username: $scope.model.username,
                        roles: $scope.model.roles,
                        primary_group_id: $scope.model.primary_group.id,
                        group_ids: $scope.model.groups.map(function(entry){return entry.id}),
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
                    if ($scope.model.password) {
                        user.password = $scope.model.password;
                    }
                    console.log(user);
                    userService.update(user, function() {
                        if (user.id == $rootScope.global.user.id) {
                            // rebuild permissions based on new roles
                            $rootScope.$broadcast("permissionsChanged");
                        }
                        $location.path("/admin/users");
                    }, function(e){
                        if (e.status == 401){
                            $location.path("/login");
                        }
                        $scope.message = e.data.message;
                    });
                }
            };

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
            }
        }
    ]);