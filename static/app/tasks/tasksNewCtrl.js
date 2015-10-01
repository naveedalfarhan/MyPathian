angular.module("pathianApp.controllers")
    .controller("tasksNewCtrl", [
        "$scope", "$rootScope", "$location", "taskService", "equipmentService","taskStatusService","taskPriorityService","taskTypeService",
        function($scope,
                 $rootScope,
                 $location,
                 taskService,
                 equipmentService,
                 taskStatusService,
                 taskPriorityService,
                 taskTypeService){
            $rootScope.global.linkpath = "#/commissioning/tasks";

            $scope.showErrorMessage = false;

            $scope.model = {
                estimated_cost:"",
                accepted_date : new Date(),
                start_date : new Date(),
                completed_date : new Date(),
                assigned_to_id: ''
            };

            $scope.assigned_to = undefined;

            $scope.submit = function(){
                if ($scope.assigned_to) {
                    $scope.model.assigned_to_id = $scope.assigned_to.id;
                }
                // Commenting this out because there doesn't appear to be a single place in the code base where the
                // commissioningGroup is getting set. I'm not sure which group is the appropriate one
                //if($rootScope.global.commissioningGroup != undefined) {
                //    $scope.model.group_id = $rootScope.global.commissioningGroup.id;
                //}
                $scope.model.group_id = $rootScope.global.user.primary_group.id
                taskService.save($scope.model, function() {
                    $location.path("/commissioning/tasks");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                });
            };

            $scope.priorities = [];
            $scope.statuses = [];
            $scope.types = [];
            $scope.equipment = [];

            taskTypeService.GetAll({}, function(response){
                $scope.types = response.data;
            });

            taskStatusService.GetAll({}, function (response) {
               $scope.statuses = response.data;
            });

            taskPriorityService.GetAll({}, function (response) {
                $scope.priorities = response.data;
            });

            equipmentService.getAllForGroup({"group_id": $scope.global.user.primary_group.id }, function (data) {
               $scope.equipment = data;
            });

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

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

            $scope.format = 'MM/dd/yyyy';

            $scope.cancel = function () {
                $location.path("/commissioning/tasks");
            }
        }
    ]);