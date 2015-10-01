angular.module("pathianApp.controllers")
    .controller("issuesNewCtrl", [
        "$scope", "$rootScope", "$location", "issueService", "equipmentService", "taskPriorityService", "taskStatusService", "taskTypeService",
        function($scope, $rootScope, $location, issueService, equipmentService, taskPriorityService, taskStatusService, taskTypeService){
            $rootScope.global.linkpath = "#/commissioning/issues";

            $scope.showErrorMessage = false;

            $scope.model = {
                name:"",
                description:"",
                equipment_id:null,
                priority_id:null,
                status_id:null,
                type_id:null,
                open_date:new Date(),
                due_date:new Date(),
                issued_by_ids: [],
                issued_to_ids: []
            };

            $scope.issued_by_selected = [];
            $scope.issued_to_selected = [];

            $scope.submit = function(){
                $scope.model.issued_by_ids = $scope.issued_by_selected.map(function (contact) { if (contact.id) {return contact.id;} return contact; });
                $scope.model.issued_to_ids = $scope.issued_to_selected.map(function (contact) { if (contact.id) {return contact.id;} return contact; });

                // The group id has changed to the primary group of the currently logged in user till I get some definition
                // on what the commissioning group is.
                $scope.model.group_id = $scope.global.user.primary_group.id;
                issueService.save($scope.model, function() {
                    $location.path("/commissioning/issues");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.open = function($event){
                $event.preventDefault();
                $event.stopPropagation();

                $scope.opened=true;
            };

            $scope.priorities = [];
            $scope.statuses = [];
            $scope.types = [];
            $scope.equipment = [];

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
                        id: { type:"string", editable:false, nullable:true, defaultValue:undefined },
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
    ]);