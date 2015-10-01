angular.module("pathianApp.controllers")
    .controller("meetingsNewCtrl", [
        "$scope", "$rootScope", "$location", "meetingtypeService",'meetingService', "projectService",
        function($scope, $rootScope, $location, meetingtypeService,meetingService, projectService) {
            $rootScope.global.linkpath = "#/commissioning/meetings";

            $scope.showErrorMessage = false;

            $scope.model = {
                called_by_id:"",
                note_taker_id:"",
                facilitator_id:"",
                time_keeper_id:"",
                attendees_ids:[],
                date: new Date()
            };

            $scope.open = function($event){
                $event.preventDefault();
                $event.stopPropagation();

                $scope.opened=true;
            };

            $scope.attendees = [];
            $scope.projects = [];
            $scope.meetingTypes = [];

            projectService.GetAll({}, function(list) {
                $scope.projects = list;
            });

            meetingtypeService.getAll(function (list) {
                $scope.meetingTypes = list.data;
            })

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

                meetingService.save($scope.model, function() {
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