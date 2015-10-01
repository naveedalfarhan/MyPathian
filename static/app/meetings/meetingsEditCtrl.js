angular.module("pathianApp.controllers")
    .controller("meetingsEditCtrl", [
        "$scope", "$rootScope", "$routeParams", "$location", "meetingService", "projectService", "meetingtypeService",
        function($scope, $rootScope, $routeParams, $location, meetingService, projectService,meetingtypeService) {
            $rootScope.global.linkpath = "#/commissioning/meetings";
            $scope.id = $routeParams.id;

            $scope.showErrorMessage = false;

            meetingService.get({id:$scope.id}, function(model) {
                $scope.model = model;
                $scope.calledby = model.called_by_model;
                $scope.notetaker = model.note_taker_model;
                $scope.facilitator = model.facilitator_model;
                $scope.timekeeper = model.time_keeper_model;
                $scope.group = model.group_model;
                $scope.attendees = model.attendees_models;
                var date = Date.parse(model.date);
                $scope.model.date = new Date(date);
            });

            $scope.open = function($event){
                $event.preventDefault();
                $event.stopPropagation();

                $scope.opened=true;
            };

            $scope.attendees = [];
            $scope.projects = [];

            projectService.GetAll({}, function(list) {
                $scope.projects = list;
            });
            meetingtypeService.getAll({}, function (list) {
                $scope.meeting_types = list.data;
            });

            $scope.submit = function() {
                if ($scope.calledby)
                    $scope.model.called_by_id = $scope.calledby.id;
                if ($scope.notetaker)
                    $scope.model.note_taker_id = $scope.notetaker.id;
                if ($scope.facilitator)
                    $scope.model.facilitator_id = $scope.facilitator.id;
                if ($scope.timekeeper)
                    $scope.model.time_keeper_id = $scope.timekeeper.id;
                if ($scope.group)
                    $scope.model.group_id = $scope.group.id;
                if ($scope.attendees)
                    $scope.model.attendees_ids = $scope.attendees.map(function(contact){ if (contact.id) return contact.id; return contact;});
                meetingService.update($scope.model, function() {
                    $location.path("/commissioning/meetings");
                }, function(e) {
                    $scope.message = e.data.message;
                    $scope.showErrorMessage = true;
                })
            };

            $scope.contactGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "Contacts",
                model: {
                    id:"id",
                    fields: {
                        id:{type:"string"},
                        full_name:{type:"string"}
                    }
                },
                columns: [
                    {
                        title:"Name",
                        field:"full_name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort: {field:"full_name", dir:"asc"}
            });

            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName:"groups",
                model:{
                    id:"id",
                    fields:{
                        id:{type:"string"},
                        name:{type:"string"}
                    }
                },
                columns:[
                    {
                        field:"name",
                        title:"Name"
                    }
                ],
                editable:false,
                createTemplate:false,
                defaultSort:{field:"name", dir:"asc"}
            });

            $scope.dateOptions = {
                'year-format':"'yy'",
                'starting-day':0
            };

            $scope.format='MM/dd/yyyy';

            $scope.cancel = function () {
                $location.path("/commissioning/meetings");
            }
        }
    ]);