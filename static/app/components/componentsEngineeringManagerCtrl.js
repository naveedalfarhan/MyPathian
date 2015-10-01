angular.module('pathianApp.controllers')
    .controller("componentsEngineeringManagerCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "$compile", "componentService", "issueService", "taskService", "componentTreeFactory",
        function($scope, $rootScope, $location, $http, $modal, $compile, componentService, issueService, taskService, componentTreeFactory) {
            $rootScope.global.linkpath = '#/admin/components';

            $scope.controlSequenceTitle = "";

            $scope.userPermissions = $rootScope.global.userPermissions;

            $scope.structureTreeOptions = {
                template: "#=item.num# #=item.description#",
                dataSource:{
                    transport: {
                        read: {
                            url: "/api/components/getStructureChildrenOf",
                            dataType: "json"
                        }
                    },
                    schema:{
                        model:{
                            id:"id",
                            hasChildren: "structure_child_ids.length > 0"
                        }
                    }
                }
            };

            var controlSequenceTransport = function GetControlSequenceTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/CS",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.controlSequenceId = undefined;
                            $scope.controlSequenceTitle = "";
                            $scope.controlSequenceDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var acceptanceRequirementTransport = function GetAcceptanceRequirementTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/AR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.acceptanceRequirementId = undefined;
                            $scope.acceptanceRequirementTitle = "";
                            $scope.acceptanceRequirementDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                }
            };

            var commissioningRequirementTransport = function GetCommissioningRequirementTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/CR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.commissioningRequirementId = undefined;
                            $scope.commissioningRequirementTitle = "";
                            $scope.commissioningRequirementDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var functionalTestTransport = function GetFunctionalTestTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/FT",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.functionalTestId = undefined;
                            $scope.functionalTestTitle = "";
                            $scope.functionalTestDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var demandResponseTransport = function GetDemandResponseTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/DR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.demandResponseId = undefined;
                            $scope.demandResponseTitle = "";
                            $scope.demandResponseDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var loadCurtailmentTransport = function GetLoadCurtailmentTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/LC",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.loadCurtailmentId = undefined;
                            $scope.loadCurtailmentTitle = "";
                            $scope.loadCurtailmentDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var maintenanceRequirementTransport = function GetMaintenanceRequirementTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/MR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.maintenanceRequirementId = undefined;
                            $scope.maintenanceRequirementTitle = "";
                            $scope.maintenanceRequirementDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var projectRequirementTransport = function GetProjectRequirementTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/PR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.projectRequirementId = undefined;
                            $scope.projectRequirementTitle = "";
                            $scope.projectRequirementDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var responsibilityTransport = function GetResponsibilityTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/paragraphs/RR",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/paragraphs/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.responsibilityId = undefined;
                            $scope.responsibilityTitle = "";
                            $scope.responsibilityDescription = "";
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var issueTransport = function GetIssueTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/issues",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/issues/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.issueId = undefined;
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            var taskTransport = function GetTaskTransport(component_id) {
                return {
                    read:{
                        url: "/api/components/" + component_id + "/tasks",
                        dataType: "json",
                        contentType:"application/json",
                        type:"GET"
                    },
                    destroy:{
                        url: function(options) {
                            return "/api/components/tasks/" + options.id;
                        },
                        dataType:"json",
                        contentType:"application/json",
                        type:"DELETE"
                    },
                    parameterMap: function(options, operation){
                        if (operation == "destroy"){
                            $scope.taskId = undefined;
                        }
                        return kendo.stringify(options);
                    }
                };
            };

            $scope.clear = function(){
                $scope.controlSequenceId = undefined;
                $scope.controlSequenceTitle = "";
                $scope.controlSequenceDescription = "";
                $("#controlSequenceTitle").focus();
                $("#controlSequenceGrid").data('kendoGrid').refresh();
            };

            $scope.clearAcceptanceRequirement = function(){
                $scope.acceptanceRequirementId = undefined;
                $scope.acceptanceRequirementTitle = "";
                $scope.acceptanceRequirementDescription = "";
                $("#acceptanceRequirementTitle").focus();
                $("#acceptanceRequirementsGrid").data('kendoGrid').refresh();
            };

            $scope.clearCommissioningRequirement = function(){
                $scope.commissioningRequirementId = undefined;
                $scope.commissioningRequirementTitle = "";
                $scope.commissioningRequirementDescription = "";
                $("#commissioningRequirementTitle").focus();
                $("#commissioningRequirementsGrid").data('kendoGrid').refresh();
            };

            $scope.clearFunctionalTest = function(){
                $scope.functionalTestId = undefined;
                $scope.functionalTestTitle = "";
                $scope.functionalTestDescription = "";
                $("#functionalTestTitle").focus();
                $("#functionalTestsGrid").data('kendoGrid').refresh();
            };

            $scope.clearDemandResponse = function(){
                $scope.demandResponseId = undefined;
                $scope.demandResponseTitle = "";
                $scope.demandResponseDescription = "";
                $("#demandResponseTitle").focus();
                $("#demandResponseGrid").data('kendoGrid').refresh();
            };

            $scope.clearLoadCurtailment = function(){
                $scope.loadCurtailmentId = undefined;
                $scope.loadCurtailmentTitle = "";
                $scope.loadCurtailmentDescription = "";
                $("#loadCurtailmentTitle").focus();
                $("#loadCurtailmentGrid").data('kendoGrid').refresh();
            };

            $scope.clearMaintenanceRequirement = function(){
                $scope.maintenanceRequirementId = undefined;
                $scope.maintenanceRequirementTitle = "";
                $scope.maintenanceRequirementDescription = "";
                $("#maintenanceRequirementTitle").focus();
                $("#maintenanceRequirementGrid").data('kendoGrid').refresh();
            };
            
            $scope.clearProjectRequirement = function(){
                $scope.projectRequirementId = undefined;
                $scope.projectRequirementTitle = "";
                $scope.projectRequirementDescription = "";
                $("#projectRequirementTitle").focus();
                $("#projectRequirementGrid").data('kendoGrid').refresh();
            };
            
            $scope.clearResponsibility = function(){
                $scope.responsibilityId = undefined;
                $scope.responsibilityTitle = "";
                $scope.responsibilityDescription = "";
                $("#responsibilityTitle").focus();
                $("#responsibilityGrid").data('kendoGrid').refresh();
            };

            

            $scope.$watch("selectedNode", function() {
                if (!$scope.selectedNode)
                    return;

                setGridOptions($scope.selectedNode.id);
            });

            $scope.controlSequenceChanged = function(e) {
                $scope.selectedControlSequence = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedControlSequence)
                    return;

                $scope.controlSequenceId = $scope.selectedControlSequence.id;
                $scope.controlSequenceTitle = $scope.selectedControlSequence.title;
                $scope.controlSequenceDescription = $scope.selectedControlSequence.description;
            };

            $scope.acceptanceRequirementChanged = function(e) {
                $scope.selectedAcceptanceRequirement = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedAcceptanceRequirement)
                    return;

                $scope.acceptanceRequirementId = $scope.selectedAcceptanceRequirement.id;
                $scope.acceptanceRequirementTitle = $scope.selectedAcceptanceRequirement.title;
                $scope.acceptanceRequirementDescription = $scope.selectedAcceptanceRequirement.description;
            };

            $scope.commissioningRequirementChanged = function(e) {
                $scope.selectedCommissioningRequirement = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedCommissioningRequirement)
                    return;

                $scope.commissioningRequirementId = $scope.selectedCommissioningRequirement.id;
                $scope.commissioningRequirementTitle = $scope.selectedCommissioningRequirement.title;
                $scope.commissioningRequirementDescription = $scope.selectedCommissioningRequirement.description;
            };

            $scope.functionalTestChanged = function(e) {
                $scope.selectedFunctionalTest = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedFunctionalTest)
                    return;

                $scope.functionalTestId = $scope.selectedFunctionalTest.id;
                $scope.functionalTestTitle = $scope.selectedFunctionalTest.title;
                $scope.functionalTestDescription = $scope.selectedFunctionalTest.description;
            };

            $scope.demandResponseChanged = function(e) {
                $scope.selectedDemandResponse = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedDemandResponse)
                    return;

                $scope.demandResponseId = $scope.selectedDemandResponse.id;
                $scope.demandResponseTitle = $scope.selectedDemandResponse.title;
                $scope.demandResponseDescription = $scope.selectedDemandResponse.description;
            };

            $scope.loadCurtailmentChanged = function(e) {
                $scope.selectedLoadCurtailment = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedLoadCurtailment)
                    return;

                $scope.loadCurtailmentId = $scope.selectedLoadCurtailment.id;
                $scope.loadCurtailmentTitle = $scope.selectedLoadCurtailment.title;
                $scope.loadCurtailmentDescription = $scope.selectedLoadCurtailment.description;
            };
            
            $scope.maintenanceRequirementChanged = function(e) {
                $scope.selectedMaintenanceRequirement = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedMaintenanceRequirement)
                    return;

                $scope.maintenanceRequirementId = $scope.selectedMaintenanceRequirement.id;
                $scope.maintenanceRequirementTitle = $scope.selectedMaintenanceRequirement.title;
                $scope.maintenanceRequirementDescription = $scope.selectedMaintenanceRequirement.description;
            };
            
            $scope.projectRequirementChanged = function(e) {
                $scope.selectedProjectRequirement = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedProjectRequirement)
                    return;

                $scope.projectRequirementId = $scope.selectedProjectRequirement.id;
                $scope.projectRequirementTitle = $scope.selectedProjectRequirement.title;
                $scope.projectRequirementDescription = $scope.selectedProjectRequirement.description;
            };
            
            $scope.responsibilityChanged = function(e) {
                $scope.selectedResponsibility = e.sender.dataItem(e.sender.select());
                if (!$scope.selectedResponsibility)
                    return;

                $scope.responsibilityId = $scope.selectedResponsibility.id;
                $scope.responsibilityTitle = $scope.selectedResponsibility.title;
                $scope.responsibilityDescription = $scope.selectedResponsibility.description;
            };

            $scope.submit = function(){
                if (!$scope.controlSequenceTitle || !$scope.controlSequenceDescription){
                    alert("Control Sequence title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.controlSequenceTitle,
                    description:$scope.controlSequenceDescription,
                    type: "CS"
                };
                if ($scope.controlSequenceId)
                    model.id = $scope.controlSequenceId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#controlSequenceGrid").data('kendoGrid').dataSource.read();
                    $("#controlSequenceGrid").data('kendoGrid').refresh();
                    $scope.clear();
                });
                return;
            };

            $scope.submitAcceptanceRequirement = function(){
                if (!$scope.acceptanceRequirementTitle || !$scope.acceptanceRequirementDescription){
                    alert("Acceptance Requirement title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.acceptanceRequirementTitle,
                    description:$scope.acceptanceRequirementDescription,
                    type: "AR"
                };
                if ($scope.acceptanceRequirementId)
                    model.id = $scope.acceptanceRequirementId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#acceptanceRequirementGrid").data('kendoGrid').dataSource.read();
                    $("#acceptanceRequirementGrid").data('kendoGrid').refresh();
                    $scope.clearAcceptanceRequirement();
                });
                return;
            };

            $scope.submitCommissioningRequirement = function(){
                if (!$scope.commissioningRequirementTitle || !$scope.commissioningRequirementDescription){
                    alert("Commissioning Requirement title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.commissioningRequirementTitle,
                    description:$scope.commissioningRequirementDescription,
                    type: "CR"
                };
                if ($scope.commissioningRequirementId)
                    model.id = $scope.commissioningRequirementId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#commissioningRequirementGrid").data('kendoGrid').dataSource.read();
                    $("#commissioningRequirementGrid").data('kendoGrid').refresh();
                    $scope.clearCommissioningRequirement();
                });
                return;
            };

            $scope.submitFunctionalTest = function(){
                if (!$scope.functionalTestTitle || !$scope.functionalTestDescription){
                    alert("Functional Test title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.functionalTestTitle,
                    description:$scope.functionalTestDescription,
                    type: "FT"
                };
                if ($scope.functionalTestId)
                    model.id = $scope.functionalTestId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#functionalTestsGrid").data('kendoGrid').dataSource.read();
                    $("#functionalTestsGrid").data('kendoGrid').refresh();
                    $scope.clearFunctionalTest();
                });
                return;
            };

            $scope.submitDemandResponse = function(){
                if (!$scope.demandResponseTitle || !$scope.demandResponseDescription){
                    alert("Demand Response title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.demandResponseTitle,
                    description:$scope.demandResponseDescription,
                    type: "DR"
                };
                if ($scope.demandResponseId)
                    model.id = $scope.demandResponseId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#demandResponseGrid").data('kendoGrid').dataSource.read();
                    $("#demandResponseGrid").data('kendoGrid').refresh();
                    $scope.clearDemandResponse();
                });
                return;
            };

            $scope.submitLoadCurtailment = function(){
                if (!$scope.loadCurtailmentTitle || !$scope.loadCurtailmentDescription){
                    alert("Load Curtailment title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.loadCurtailmentTitle,
                    description:$scope.loadCurtailmentDescription,
                    type: "LC"
                };
                if ($scope.loadCurtailmentId)
                    model.id = $scope.loadCurtailmentId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#loadCurtailmentGrid").data('kendoGrid').dataSource.read();
                    $("#loadCurtailmentGrid").data('kendoGrid').refresh();
                    $scope.clearLoadCurtailment();
                });
                return;
            };
            
            $scope.submitMaintenanceRequirement = function(){
                if (!$scope.maintenanceRequirementTitle || !$scope.maintenanceRequirementDescription){
                    alert("Maintenance Requirements title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.maintenanceRequirementTitle,
                    description:$scope.maintenanceRequirementDescription,
                    type: "MR"
                };
                if ($scope.maintenanceRequirementId)
                    model.id = $scope.maintenanceRequirementId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#maintenanceRequirementGrid").data('kendoGrid').dataSource.read();
                    $("#maintenanceRequirementGrid").data('kendoGrid').refresh();
                    $scope.clearMaintenanceRequirement();
                });
                return;
            };
            
            $scope.submitProjectRequirement = function(){
                if (!$scope.projectRequirementTitle || !$scope.projectRequirementDescription){
                    alert("Project Requirements title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.projectRequirementTitle,
                    description:$scope.projectRequirementDescription,
                    type: "PR"
                };
                if ($scope.projectRequirementId)
                    model.id = $scope.projectRequirementId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#projectRequirementGrid").data('kendoGrid').dataSource.read();
                    $("#projectRequirementGrid").data('kendoGrid').refresh();
                    $scope.clearProjectRequirement();
                });
                return;
            };
            
            $scope.submitResponsibility = function(){
                if (!$scope.responsibilityTitle || !$scope.responsibilityDescription){
                    alert("Roles and Responsibilities title and description are required.");
                    return;
                }
                var model  = {
                    component_id:$scope.selectedNode.id,
                    title:$scope.responsibilityTitle,
                    description:$scope.responsibilityDescription,
                    type: "RR"
                };
                if ($scope.responsibilityId)
                    model.id = $scope.responsibilityId;
                else
                    model.id = 0;
                componentService.addParagraph(model, function(data){
                    $("#responsibilityGrid").data('kendoGrid').dataSource.read();
                    $("#responsibilityGrid").data('kendoGrid').refresh();
                    $scope.clearResponsibility();
                });
                return;
            };

            $scope.submitIssue = function(){
                var model  = {
                    component_id:$scope.selectedNode.id,
                    issue_id:$scope.selectedIssue.id
                };
                componentService.addIssue({component_id: model.component_id}, model, function(data){
                    var issueGrid = $("#issueGrid");
                    issueGrid.data('kendoGrid').dataSource.read();
                    issueGrid.data('kendoGrid').refresh();

                    loadAvailableIssues();
                });

                return;
            };

            $scope.submitTask = function(){
                var model  = {
                    component_id:$scope.selectedNode.id,
                    task_id:$scope.selectedTask.id
                };
                componentService.addTask({component_id: model.component_id}, model, function(data){
                    var taskGrid = $("#taskGrid");
                    taskGrid.data('kendoGrid').dataSource.read();
                    taskGrid.data('kendoGrid').refresh();

                    loadAvailableTasks();
                });

                return;
            };

            function setGridOptions(component_id){
                if (!component_id)
                    component_id = 0;

                $scope.controlSequenceGridOptions = getGridOptions(component_id, controlSequenceTransport);
                $scope.acceptanceRequirementGridOptions = getGridOptions(component_id, acceptanceRequirementTransport);
                $scope.commissioningRequirementGridOptions = getGridOptions(component_id, commissioningRequirementTransport);
                $scope.functionalTestsGridOptions = getGridOptions(component_id, functionalTestTransport);
                $scope.demandResponseGridOptions = getGridOptions(component_id, demandResponseTransport);
                $scope.loadCurtailmentGridOptions = getGridOptions(component_id, loadCurtailmentTransport);
                $scope.maintenanceRequirementGridOptions = getGridOptions(component_id, maintenanceRequirementTransport);
                $scope.projectRequirementGridOptions = getGridOptions(component_id, projectRequirementTransport);
                $scope.responsibilityGridOptions = getGridOptions(component_id, responsibilityTransport);
                
                var issueGridOptions = getGridOptions(component_id, issueTransport);
                issueGridOptions.columns[1].command.push(
                    {
                        name: "edit",
                        click: function(e) {
                            var id = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr")).id;
                            alert("issue: " + id);
                            return false;
                        }
                    }
                );
                $scope.issueGridOptions = issueGridOptions;

                $scope.taskGridOptions = getGridOptions(component_id, taskTransport);
            }

            function getGridOptions(component_id, transport) {
                return {
                    dataSource:{
                        transport: transport(component_id),
                        schema:{
                            data: "data",
                            total: "total",
                            model: {
                                id:"id",
                                fields:{
                                    id: { type:"string"},
                                    title: {type:"string"},
                                    description: {type:"string"}
                                }
                            }
                        },
                        pageSize: 10,
                        serverPaging: true
                    },
                    scrollable:false,
                    filterable:false,
                    sortable:false,
                    pageable:true,
                    selectable:"single",
                    toolbar:false,
                    editable:"popup",
                    columns: [
                        {
                            field:"title",
                            title:"Title"
                        },
                        {
                            command:[
                                {
                                    name:"destroy"
                                }
                            ]
                        }
                    ]
                }
            }

            setGridOptions();
        }
    ]);