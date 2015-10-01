angular.module("pathianApp.controllers")
    .controller("issuesEditCtrl", [
        "$scope", "$rootScope", "$location", "$routeParams", "issueService", "equipmentService", "taskPriorityService", "taskStatusService", "taskTypeService",
        function($scope, $rootScope, $location, $routeParams, issueService, equipmentService,taskPriorityService, taskStatusService, taskTypeService) {
            $rootScope.global.linkpath = "#/commissioning/issues";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            $scope.model = issueService.get({id:$scope.id}, function(model) {
                $scope.model = model;

                var date = Date.parse(model.open_date);
                $scope.model.open_date = new Date(date);

                date = Date.parse(model.due_date);
                $scope.model.due_date = new Date(date);

                $scope.issued_by_selected = model.issued_by_model;
                $scope.issued_to_selected = model.issued_to_model;
            });

            $scope.equipment = [];

            $scope.submit = function(){
                $scope.model.issued_by_ids = $scope.issued_by_selected.map(function(contact) { if (contact.id) {return contact.id;} return contact; });
                $scope.model.issued_to_ids = $scope.issued_to_selected.map(function(contact) { if (contact.id) {return contact.id;} return contact; });
                // The group id has changed to the primary group of the currently logged in user till I get some definition
                // on what the commissioning group is.
                $scope.model.group_id = $scope.global.user.primary_group.id;
                issueService.update($scope.model, function() {
                    $location.path("/commissioning/issues");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            // The group id has changed to the primary group of the currently logged in user till I get some definition
            // on what the commissioning group is.
            equipmentService.getAllForGroup({"group_id": $scope.global.user.primary_group.id }, function (data) {
               $scope.equipment = data;
            });

            taskPriorityService.GetAll({}, function (response) {
                $scope.priorities = response.data;
            });

            taskStatusService.GetAll({}, function (response) {
                $scope.statuses = response.data;
            });

            taskTypeService.GetAll({}, function (response) {
                $scope.types = response.data;
            });

            $scope.contactGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName:"Contacts",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string", editable:false, nullable:true, defaultValue:undefined},
                        full_name:{type:"string"}
                    }
                },
                columns:[{
                    title:"Name",
                    field:"full_name"
                }],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"last_name", dir:"asc"}
            });

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format='MM/dd/yyyy';

            $scope.cancel = function () {
                $location.path("/commissioning/issues");
            }
        }
    ])