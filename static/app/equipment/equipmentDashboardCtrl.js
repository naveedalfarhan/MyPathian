angular.module('pathianApp.controllers')
    .controller("equipmentDashboardCtrl", [
        "$scope", 
        "$rootScope", 
        "$routeParams", 
        "$location", 
        "$http", 
        "$modal", 
        "$compile", 
        "$q", 
        "equipmentService",
        "equipmentTaskManagementService",
        "taskTableData", 
        "componentService", 
        "issueService",
        "equipmentIssueManagementService",
        "issueTableData", 
        "taskService", 
        "resetScheduleService", 
        "componentTreeFactory", 
        "toaster", 
        "dataMappingService",
        "syrxCategoryService",
        "equipmentDashboardPointManagementService",
        function(
            $scope, 
            $rootScope, 
            $routeParams, 
            $location, 
            $http, 
            $modal, 
            $compile, 
            $q, 
            equipmentService,
            equipmentTaskManagementService,
            taskTableData, 
            componentService, 
            issueService,
            equipmentIssueManagementService,
            issueTableData, 
            taskService, 
            resetScheduleService, 
            componentTreeFactory, 
            toaster, 
            dataMappingService,
            syrxCategoryService,
            equipmentDashboardPointManagementService) {

            $rootScope.global.linkpath = '#/commissioning/equipment';
            $scope.equipmentId = $routeParams.id;

            //dialogs
            $scope.editWindow;
            $scope.previewWindow;

            //new and edit form fields
            $scope.isEditing = false;
            $scope.isCreating = false;
            $scope.currentNewItemType = "";
            $scope.currentItemInEdit = {};
            $scope.paragraphTitle = "";
            $scope.paragraphContent = "";

            $scope.previewContent = "<div>this is a test</div>";

            $scope.viewModel = {};

            $scope.rafPressures = [];

            $scope.selectedResetSchedule = {};
            $scope.availableResetSchedules = [];
            $scope.resetSchedules = [];

            $scope.controlSequenceComponents = [];
            $scope.acceptanceRequirementComponents = [];
            $scope.commissioningRequirementComponents = [];
            $scope.functionalTestComponents = [];
            $scope.demandResponseComponents = [];
            $scope.loadCurtailmentComponents = [];
            $scope.maintenanceRequirementComponents = [];
            $scope.projectRequirementComponents = [];
            $scope.responsibilityComponents = [];

            $scope.selectedPredefinedIssue = {};
            $scope.predefinedIssues = [];
            $scope.equipmentIssues = [];

            $scope.selectedPredefinedTask = {};
            $scope.predefinedTasks = [];
            $scope.equipmentTasks = [];

            $scope.syrxCategoriesPromise = syrxCategoryService.GetAll().$promise;

            $scope.numericPoints = [];

            equipmentService.get({ id: $scope.equipmentId }, function(model) {
                $scope.model = model;
                if (!$scope.model.component)
                    $scope.model.component = null;
                $scope.viewModel.group = $scope.model.group;
                $scope.viewModel.component = $scope.model.component;
                $scope.viewModel.subcomponents = $scope.model.subcomponents;
                $scope.viewModel.points = $scope.model.points;

                $scope.viewModel.paragraphs = $scope.model.paragraphs;

            });

            equipmentService.getMappedPoints({equipment_id: $scope.equipmentId}, function(data) {
                $scope.viewModel.syrx_nums = [];
                data.forEach(function(equipmentPoint){
                    $scope.viewModel.syrx_nums.push({'num': equipmentPoint.syrx_num, 'name': equipmentPoint.description});
                });

                // add the 'all' option to the list
                $scope.viewModel.syrx_nums.unshift({'num': 'all', 'name': '-- All Equipment Points --'});


                if ($scope.viewModel.syrx_nums.length > 0) {
                    $scope.chartModel = {
                        start_month: 1,
                        end_month: 12,
                        report_year: new Date().getFullYear(),
                        comparison_year: new Date().getFullYear() - 1,
                        syrx_num: "all",
                        equipment_id: $scope.equipmentId
                    };
                }

                $scope.tableModel = {
                    report_year: new Date().getFullYear(),
                    comparison_year: new Date().getFullYear() - 1,
                    equipment_id: $scope.equipmentId
                };
            });

            $scope.years = [];
            var currentYear = new Date().getFullYear();
            for (var yr = 0; yr <= 10; yr++) {
                $scope.years.push(currentYear - yr);
            }


            $scope.tabActivated = function(e) {
                var type = $(e.item).attr("data-paragraph-type");
                var name = $(e.item).attr("data-name");

                kendo.ui.progress($(".pat-container"), true);
                $scope.mappingPoint = undefined;

                if (type) {
                    if (type === "RA") {
                        loadRafTab();
                    }
                    else if (type === "RS") {
                        loadResetScheduleTab();
                    }
                    else if (type === "IS") {
                        loadIssuesTab();
                    }
                    else if (type === "TA") {
                        loadTasksTab();
                    }
                    else {
                        loadParagraphTab(type);
                    }
                } else if (name == "pointMappings") {
                    $scope.refreshVendorPoints();
                    kendo.ui.progress($(".pat-container"), false);
                } else if (name == "numericPoints") {
                    $scope.refreshNumericPoints();
                }
            };

            $scope.moveItemUp = function(item) {
                var componentArray = getComponentArray(item.type);

                if (item.sort_order === 1) {
                    return;
                }

                var currentComponent = _.find(componentArray, function(component) {
                    return component.componentName === item.component_full_name;
                });

                if (!currentComponent) {
                    return;
                }

                var currentCategory = _.find(currentComponent.categories, function(category) {
                    return category.categoryName === item.category_name;
                });

                if (!currentCategory) {
                    return;
                }

                //try to find the next item in sort order
                var nextItem = _.find(currentCategory.items, function(currentItem) {
                    return (item.sort_order - 1) === currentItem.sort_order;
                });

                kendo.ui.progress($(".pat-container"), true);
                equipmentService.moveParagraphUp({equipment_id: $scope.equipmentId, paragraph_id: item.id}, function(response) {
                    //set the item to the current items sort order if we find it
                    if (nextItem) {
                        nextItem.sort_order = item.sort_order;
                        
                        //update current item sort order
                        item.sort_order -= 1;
                    }
                }, function(httpResponse){
                    toaster.pop('error', "Re Order Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.moveItemDown = function(item) {
                var componentArray = getComponentArray(item.type);

                var currentComponent = _.find(componentArray, function(component) {
                    return component.componentName === item.component_full_name;
                });

                if (!currentComponent) {
                    return;
                }

                var currentCategory = _.find(currentComponent.categories, function(category) {
                    return category.categoryName === item.category_name;
                });

                if (!currentCategory) {
                    return;
                }

                if (item.sort_order >= currentCategory.items.length) {
                    return;
                }

                //try to find the next item in sort order
                var nextItem = _.find(currentCategory.items, function(currentItem) {
                    return (item.sort_order + 1) === currentItem.sort_order;
                });

                kendo.ui.progress($(".pat-container"), true);
                equipmentService.moveParagraphDown({equipment_id: $scope.equipmentId, paragraph_id: item.id}, function(response) {
                    //set the item to the current items sort order if we find it
                    if (nextItem) {
                        nextItem.sort_order = item.sort_order;

                        //update current item sort order
                        item.sort_order += 1;
                    }
                }, function(httpResponse){
                    toaster.pop('error', "Re Order Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.previewClicked = function(type) {
                var modalInstance = $modal.open({
                    templateUrl: 'previewModal',
                    controller: PreviewModalCtrl,
                    resolve: {
                        content: function(){return getPreview(type);}
                    }
                });
            };

            $scope.addParagraphClicked = function(type) {
                $scope.syrxCategoriesPromise.then(function(syrxCategories) {
                    var modalInstance = $modal.open({
                        templateUrl: 'addParagraphModal',
                        controller: AddParagraphModalCtrl,
                        resolve: {
                            categories: function(){return syrxCategories;},
                            type: function(){return type;},
                            component_id: function(){return $scope.viewModel.component.id;}
                        }
                    });

                    modalInstance.result.then(function (result) {
                        kendo.ui.progress($(".pat-container"), true);
                        equipmentService.addParagraph({equipment_id: $scope.equipmentId, paragraph_id: result}, function(response){
                            loadParagraphTab(type);
                            toaster.pop('success', "Success", "Paragraph Added Successfully.")
                        }, function(httpResponse){
                            toaster.pop('error', "Add paragraph failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                        }).$promise.finally(function(){
                            kendo.ui.progress($(".pat-container"), false);
                        });
                    });
                });
            };

            $scope.newRafClicked = function() {
                var modalInstance = $modal.open({
                    templateUrl: 'rafModal',
                    controller: RafModalCtrl
                });

                modalInstance.result.then(function (result) {
                    rafSubmit(result);
                });
            };

            $scope.editItem = function(item) {
                var modalInstance = $modal.open({
                    templateUrl: 'editModal',
                    controller: EditModalCtrl,
                    resolve: {
                        title: function(){return item.title;},
                        content: function(){return item.description;}
                    }
                });

                modalInstance.result.then(function (result) {
                    $scope.paragraphTitle = result.title;
                    $scope.paragraphContent = result.content;
                    editSubmit(item);
                });
            };

            function editSubmit(item) {
                //create base model
                var model  = {
                    equipment_id:$scope.equipmentId,
                    title:$scope.paragraphTitle,
                    description:$scope.paragraphContent,
                };

                model.id = item.id;
                model.type = item.type;
                model.sort_order = item.sort_order;

                kendo.ui.progress($(".pat-container"), true);
                equipmentService.updateParagraph(model, function(data){
                    item.title = $scope.paragraphTitle;
                    item.description = $scope.paragraphContent;

                    resetDialog();

                    toaster.pop('success', "Success", "Paragraph Updated Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Update Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function rafSubmit(raf) {
                raf.equipment_id = $scope.equipmentId;

                kendo.ui.progress($(".pat-container"), true);
                equipmentService.insertRafPressure(raf, function(data){
                    raf.id = data.id;
                    $scope.rafPressures.push(raf);

                    toaster.pop('success', "Success", "RAF Pressure Inserted Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Update Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            $scope.deleteItem = function(item) {
                kendo.ui.progress($(".pat-container"), true);
                equipmentService.deleteParagraph({equipment_id: $scope.equipmentId, paragraph_id: item.id}, function(response) {
                    loadParagraphTab(item.type);
                    toaster.pop('success', "Success", "Paragraph Deleted Successfully.")
                }, function(httpResponse) {
                    kendo.ui.progress($(".pat-container"), false);
                    toaster.pop('error', "Delete Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                });
            };

            $scope.deleteRaf = function(rafId) {
                var r = confirm("Are you sure you want to delete this RAF Pressure?");
                if (r == true) {
                    kendo.ui.progress($(".pat-container"), true);
                    equipmentService.deleteRafPressure({raf_id: rafId}, function(result) {
                        var deletedRaf = _.find($scope.rafPressures, function(raf) {
                            return raf.id === rafId;
                        });

                        if (deletedRaf) {
                            var index = $scope.rafPressures.indexOf(deletedRaf);

                            if (index > -1) {
                                $scope.rafPressures.splice(index, 1);
                            }
                        }

                        toaster.pop('success', "Success", "RAF Pressure Deleted Successfully.")
                    }, function(httpResponse) {
                        toaster.pop('error', "Delete Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                    }).$promise.finally(function() {
                        kendo.ui.progress($(".pat-container"), false);
                    });
                }
            };

            $scope.addResetSchedule = function() {
                kendo.ui.progress($(".pat-container"), true);
                equipmentService.insertResetSchedule({equipment_id: $scope.equipmentId, reset_schedule_id: $scope.selectedResetSchedule.id}, function(response) {
                    var index = $scope.availableResetSchedules.indexOf($scope.selectedResetSchedule);

                    if (index > -1) {
                        $scope.availableResetSchedules.splice(index, 1);
                        $scope.resetSchedules.push($scope.selectedResetSchedule);
                    }

                    toaster.pop('success', "Success", "Reset Schedule Added Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.deleteResetSchedule = function(resetSchedule) {
                kendo.ui.progress($(".pat-container"), true);
                equipmentService.deleteResetSchedule({equipment_id: $scope.equipmentId, reset_schedule_id: resetSchedule.id}, function(response) {
                    var index = $scope.resetSchedules.indexOf(resetSchedule);

                    if (index > -1) {
                        $scope.resetSchedules.splice(index, 1);
                        $scope.availableResetSchedules.push(resetSchedule);
                    }

                    toaster.pop('success', "Success", "Reset Schedule Deleted Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Delete Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.addEquipmentIssue = function() {
                kendo.ui.progress($(".pat-container"), true);
                var predefinedIssue = $scope.selectedPredefinedIssue;

                var equipmentIssue = {
                    title: predefinedIssue.title,
                    description: predefinedIssue.description,
                    group_id: $scope.viewModel.group.id,
                    equipment_id: $scope.equipmentId,
                    priority_id: predefinedIssue.priority_id,
                    status_id: predefinedIssue.status_id,
                    type_id: predefinedIssue.type_id,
                };
                equipmentService.insertEquipmentIssue(equipmentIssue, function(response) {
                    equipmentIssue.id = response.id;

                    $scope.equipmentIssues.push(equipmentIssue);

                    toaster.pop('success', "Success", "Equipment Issue Added Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.createEquipmentIssue = function() {
                var issueModel = {};

                getIssueTableData().then(function(issueData) {
                    equipmentIssueManagementService.launchComponentIssueEditor(issueModel, $scope.equipmentId, issueData, function(equipmentIssue) {
                        $scope.equipmentIssues.push(equipmentIssue)
                    });
                });
            };

            $scope.editEquipmentIssue = function(issue) {
                getIssueTableData().then(function(issueData) {
                    equipmentIssueManagementService.launchComponentIssueEditor(issue, $scope.equipmentId, issueData, function(equipmentIssue) {
                        issue.title = equipmentIssue.title;
                        issue.type_id = equipmentIssue.type_id;
                        issue.status_id = equipmentIssue.status_id;
                        issue.priority_id = equipmentIssue.priority_id;
                        issue.open_date = equipmentIssue.open_date;
                        issue.due_date = equipmentIssue.due_date;
                        issue.description = equipmentIssue.description;
                    });
                });
            };

            $scope.deleteEquipmentIssue = function(issue) {
                kendo.ui.progress($(".pat-container"), true);
                equipmentService.deleteEquipmentIssue({equipment_id: issue.equipment_id, equipment_issue_id: issue.id}, function(response) {
                    var index = $scope.equipmentIssues.indexOf(issue);

                    if (index > -1) {
                        $scope.equipmentIssues.splice(index, 1);
                    }

                    toaster.pop('success', "Success", "Equipment Issue Deleted Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.addEquipmentTask = function() {
                kendo.ui.progress($(".pat-container"), true);
                var predefinedTask = $scope.selectedPredefinedTask;

                var equipmentTask = {
                    title: predefinedTask.title,
                    description: predefinedTask.description,
                    group_id: $scope.viewModel.group.id,
                    equipment_id: $scope.equipmentId,
                    priority_id: predefinedTask.priority_id,
                    status_id: predefinedTask.status_id,
                    type_id: predefinedTask.type_id,
                };
                equipmentService.insertEquipmentTask(equipmentTask, function(response) {
                    equipmentTask.id = response.id;

                    $scope.equipmentTasks.push(equipmentTask);

                    toaster.pop('success', "Success", "Equipment Task Added Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.createEquipmentTask = function() {
                var taskModel = {};

                getTaskTableData().then(function(taskData) {
                    equipmentTaskManagementService.launchComponentTaskEditor(taskModel, $scope.equipmentId, taskData, function(equipmentTask) {
                        $scope.equipmentTasks.push(equipmentTask)
                    });
                });
            };

            $scope.editEquipmentTask = function(task) {
                getTaskTableData().then(function(taskData) {
                    equipmentTaskManagementService.launchComponentTaskEditor(task, $scope.equipmentId, taskData, function(equipmentTask) {
                        $scope.equipmentTasks.push(equipmentTask)
                    });
                });
            };

            $scope.deleteEquipmentTask = function(task) {
                kendo.ui.progress($(".pat-container"), true);
                equipmentService.deleteEquipmentTask({equipment_id: task.equipment_id, equipment_task_id: task.id}, function(response) {
                    var index = $scope.equipmentTasks.indexOf(task);

                    if (index > -1) {
                        $scope.equipmentTasks.splice(index, 1);
                    }

                    toaster.pop('success', "Success", "Equipment Task Deleted Successfully.")
                }, function(httpResponse) {
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            function getIssueTableData() {
                if (!$scope.issueTableData) {
                    $scope.issueTableData = issueTableData();    
                }

                return $scope.issueTableData;
            }

            function getTaskTableData() {
                if (!$scope.taskTableData) {
                    $scope.taskTableData = taskTableData();    
                }

                return $scope.taskTableData;
            }

            function getPreview(type) {
                var components = _.sortBy(getComponentArray(type), function(comp) {
                    return comp.componentName;
                });

                var html = "";

                _.each(components, function(component) {
                    html += "<h2>" + component.componentName + "</h2>"

                    var sortedCategories = _.sortBy(component.categories, function(cat) {
                        return cat.categoryName;
                    });

                    _.each(sortedCategories, function(cat) {
                        html += "<h3>" + cat.categoryName + "</h3>"

                        var sortedItems = _.sortBy(cat.items, function(item) {
                            return item.sort_order;
                        });

                        _.each(sortedItems, function(item) {
                            html += "<h4>" + item.title + "</h4>"
                            html += item.description;
                        });
                    });
                });

                return html;
            }

            function resetDialog() {
                $scope.isEditing = false;
                $scope.isCreating = false;
                $scope.currentNewItemType = "";
                $scope.currentItemInEdit = {};
                $scope.paragraphTitle = "";
                $scope.paragraphContent = "";
            }

            function getComponentArray(type) {
                var componentArray;

                if (type === "CS") {
                    componentArray = $scope.controlSequenceComponents;
                }
                if (type === "AR") {
                    componentArray = $scope.acceptanceRequirementComponents;
                }
                if (type === "CR") {
                    componentArray = $scope.commissioningRequirementComponents;
                }
                if (type === "FT") {
                    componentArray = $scope.functionalTestComponents;
                }
                if (type === "DR") {
                    componentArray = $scope.demandResponseComponents;
                }
                if (type === "LC") {
                    componentArray = $scope.loadCurtailmentComponents;
                }
                if (type === "MR") {
                    componentArray = $scope.maintenanceRequirementComponents;
                }
                if (type === "PR") {
                    componentArray = $scope.projectRequirementComponents;
                }
                if (type === "RR") {
                    componentArray = $scope.responsibilityComponents;
                }

                return componentArray;
            }

            function loadParagraphTab(type) {
                var componentArray = getComponentArray(type);

                componentArray.length = 0;

                kendo.ui.progress($(".pat-container"), true);
                equipmentService.getAllParagraphsForType({equipment_id: $scope.equipmentId, type: type}, function(response) {
                    items = response.results;

                    var components = [];
                    var componentNames = _.uniq(_.pluck(items, "component_full_name"));

                    _.each(componentNames, function(componentName) {
                        var component = {
                            componentName: componentName,
                            categories: []
                        };
                        var itemsInComponent = _.filter(items, function(item) {
                            return item.component_full_name === componentName;
                        });

                        var categoriesInComponent = _.uniq(_.pluck(itemsInComponent, "category_name"));

                        _.each(categoriesInComponent, function(categoryName) {
                            var itemsInCategoryAndComponent = _.filter(items, function(item) {
                                return item.category_name === categoryName && item.component_full_name === componentName;
                            });

                            var category = {
                                categoryName: categoryName,
                                items: itemsInCategoryAndComponent
                            };

                            component.categories.push(category);
                        });

                        components.push(component);
                    });

                    _.each(components, function(component) {
                        componentArray.push(component);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function loadIssuesTab() {
                kendo.ui.progress($(".pat-container"), true);

                var predefinedIssuesPromise = componentService.getComponentIssues({component_id: $scope.viewModel.component.id}, function(response) {
                    _.each(response.results, function(issue) {
                        $scope.predefinedIssues.push(issue);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Predefined Issue Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occurred fetching predefined issues")
                }).$promise;

                var equipmentIssuesPromise = equipmentService.getEquipmentIssues({equipment_id: $scope.equipmentId}, function(response) {
                    $scope.equipmentIssues.length = 0;
                    _.each(response.results, function(issue) {
                        $scope.equipmentIssues.push(issue);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Equipment Issue Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occurred fetching issues")
                }).$promise;

                $q.all([predefinedIssuesPromise, equipmentIssuesPromise]).finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function loadTasksTab() {
                kendo.ui.progress($(".pat-container"), true);

                var predefinedTasksPromise = componentService.getComponentTasks({component_id: $scope.viewModel.component.id}, function(response) {
                    _.each(response.results, function(task) {
                        $scope.predefinedTasks.push(task);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Predefined Task Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occurred fetching predefined tasks")
                }).$promise;

                var equipmentTasksPromise = equipmentService.getEquipmentTasks({equipment_id: $scope.equipmentId}, function(response) {
                    $scope.equipmentTasks.length = 0;
                    _.each(response.results, function(task) {
                        $scope.equipmentTasks.push(task);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Equipment Task Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occurred fetching tasks")
                }).$promise;

                $q.all([predefinedTasksPromise, equipmentTasksPromise]).finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function loadRafTab() {
                $scope.rafPressures.length = 0;

                equipmentService.getRafPressures({equipment_id: $scope.equipmentId}, function(response) {
                    rafs = response.results;

                    _.each(rafs, function(raf) {
                        $scope.rafPressures.push(raf);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "RAF Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occured while fetching RAF pressures")
                }).$promise.finally(function(){
                    kendo.ui.progress($(".pat-container"), false);
                });
            }

            function loadResetScheduleTab() {
                var allResetSchedules = [];
                var assignedResetScheduleIds = [];

                kendo.ui.progress($(".pat-container"), true);
                var rsPromise = resetScheduleService.GetAll(function(response) {
                    $scope.availableResetSchedules.length = 0;
                    _.each(response.results, function (resetSchedule) {
                        allResetSchedules.push(resetSchedule);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Reset Schedule Fetch Failed", "An error occured while fetching reset schedules")
                }).$promise;

                $scope.resetSchedules.length = 0;
                var eqPromise = equipmentService.getResetSchedules({equipment_id: $scope.equipmentId}, function(response) {
                    _.each(response.results, function(resetSchedule) {
                        assignedResetScheduleIds.push(resetSchedule);
                    });
                }, function(httpResponse) {
                    toaster.pop('error', "Equipment Reset Schedule Fetch Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occured while fetching equipment reset schedules")
                }).$promise;

                $q.all([rsPromise, eqPromise]).then(function() {
                    _.each(allResetSchedules, function(resetSchedule) {
                        if (_.contains(assignedResetScheduleIds, resetSchedule.id)) {
                            $scope.resetSchedules.push(resetSchedule);
                        } else {
                            $scope.availableResetSchedules.push(resetSchedule);
                        }
                    });
                    kendo.ui.progress($(".pat-container"), false);
                }).finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            }


            $scope.refreshVendorPoints = function() {
                if ($("#mappedPointsGrid").data("kendoGrid"))
                    $("#mappedPointsGrid").data("kendoGrid").dataSource.read();
                if ($("#unmappedPointsGrid").data("kendoGrid"))
                    $("#unmappedPointsGrid").data("kendoGrid").dataSource.read();
            };

            $scope.refreshVendorPoints();

            $scope.mapPoint = function(syrx_num) {
                $scope.mappingPoint = syrx_num;
            };

            $scope.mapPointToJohnson = function(johnson_point) {
                kendo.ui.progress($(".pat-container"), true);
                var mapping = {
                    johnson_site_id: johnson_point.johnson_site_id,
                    johnson_fqr: johnson_point.johnson_fqr,
                    syrx_num: $scope.mappingPoint,
                    global: johnson_point.global
                };
                dataMappingService.insertJohnson(mapping, function() {
                    $scope.mappingPoint = undefined;
                    $scope.refreshVendorPoints();
                    kendo.ui.progress($(".pat-container"), false);
                }, function(httpResponse) {
                    toaster.pop('error', "Mapping Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occured while inserting the johnson point.")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.mapPointToFieldserver = function(fieldserver_point) {
                kendo.ui.progress($(".pat-container"), true);
                var mapping = {
                    fieldserver_site_id: fieldserver_point.fieldserver_site_id,
                    fieldserver_offset: fieldserver_point.fieldserver_offset,
                    syrx_num: $scope.mappingPoint,
                    global: fieldserver_point.global
                };
                dataMappingService.insertFieldserver(mapping, function() {
                    $scope.mappingPoint = undefined;
                    $scope.refreshVendorPoints();
                }, function(httpResponse) {
                    toaster.pop('error', "Mapping Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occured while inserting the fieldserver point.")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.mapPointToInvensys = function(invensys_point) {
                kendo.ui.progress($(".pat-container"), true);
                var mapping = {
                    invensys_site_name: invensys_point.invensys_site_name,
                    invensys_equipment_name: invensys_point.invensys_equipment_name,
                    invensys_point_name: invensys_point.invensys_point_name,
                    syrx_num: $scope.mappingPoint,
                    global: invensys_point.global
                };
                dataMappingService.insertInvensys(mapping, function() {
                    $scope.mappingPoint = undefined;
                    $scope.refreshVendorPoints();
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.mapPointToSiemens = function(siemens_point) {
                kendo.ui.progress($(".pat-container"), true);
                var mapping = {
                    siemens_meter_name: siemens_point.siemens_meter_name,
                    syrx_num: $scope.mappingPoint,
                    global: siemens_point.global
                };
                dataMappingService.insertSiemens(mapping, function () {
                    $scope.mappingPoint = undefined;
                    $scope.refreshVendorPoints();
                }, function(httpResponse) {
                    toaster.pop('error', "Mapping Failed", httpResponse.data.Message ? httpResponse.data.Message : "An error occurred while inserting the Siemens point.")
                }).$promise.finally(function() {
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

            $scope.mappedPointsGridOptions = {
                dataSource: {
                    transport: {
                        read: {url: "/api/equipment/" + $scope.equipmentId + "/mapped_points_grid", dataType: "json", contentType: "application/json", type: "GET"}
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                syrx_num: { type: "string"}
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                }, scrollable: false, filterable: true, sortable: false, pageable: true,
                columns: [
                    {field:"syrx_num",title:"Syrx num"},
                    {
                        field: "",
                        title: "Description",
                        template: "#if(source=='johnson'){# Johnson - #=johnson_site_id#/#=johnson_fqr# #}else if(source=='fieldserver'){# Fieldserver - #=fieldserver_site_id#[#=fieldserver_offset#] #}else if(source=='invensys'){# Invensys - #=invensys_site_name#/#=invensys_equipment_name#/#=invensys_point_name# #}else if(source=='siemens'){# Siemens - #=siemens_meter_name# #}#"
                    },
                    {
                        command:
                        [{
                            name: "Unmap",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                $scope.$apply(function() {
                                    equipmentDashboardPointManagementService.launchPointUnmapConfirmation(dataItem, function(){
                                        $scope.refreshVendorPoints()
                                    });
                                });
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.unmappedPointsGridOptions = {
                dataSource: {
                    transport: {
                        read: {url: "/api/equipment/" + $scope.equipmentId + "/unmapped_points_grid", dataType: "json", contentType: "application/json", type: "GET"}
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                syrx_num: { type: "string"}
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                }, scrollable: false, filterable: true, sortable: false, pageable: true,
                columns: [
                    {field:"syrx_num",title:"Syrx num"},
                    {
                        command:
                        [{
                            name: "Map",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                $scope.$apply(function() {
                                    $scope.mapPoint(dataItem.syrx_num);
                                });
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.johnsonUnknownGridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/unknownJohnson",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                johnson_site_id: { type: "string"},
                                johnson_fqr: { type: "string" },
                                global: { type: 'boolean' }
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                },
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {field:"johnson_site_id",title:"Johnson Site Id"},
                    {field:"johnson_fqr",title:"Johnson FQR"},
                    {
                        command:
                        [{
                            name: "Map",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                if (!dataItem.global) {
                                    equipmentDashboardPointManagementService.launchGlobalPointConfirmation(dataItem, function(returnDataItem){
                                        dataItem = returnDataItem;
                                        $scope.mapPointToJohnson(dataItem);
                                    });
                                } else {
                                    $scope.$apply(function() {
                                        $scope.mapPointToJohnson(dataItem);
                                    });
                                }
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.fieldserverUnknownGridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/unknownFieldserver",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                fieldserver_site_id: { type: "string"},
                                fieldserver_offset: { type: "number" },
                                global: {type: 'boolean'}
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                },
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {field:"fieldserver_site_id",title:"Fieldserver Site Id"},
                    {field:"fieldserver_offset",title:"Fieldserver Offset"},
                    {
                        command:
                        [{
                            name: "Map",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                if (!dataItem.global) {
                                    equipmentDashboardPointManagementService.launchGlobalPointConfirmation(dataItem, function(returnDataItem){
                                        dataItem = returnDataItem;
                                        $scope.mapPointToFieldserver(dataItem);
                                    });
                                } else {
                                    $scope.$apply(function() {
                                        $scope.mapPointToFieldserver(dataItem);
                                    });
                                }
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.invensysUnknownGridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/unknownInvensys",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                invensys_site_name: { type: "string"},
                                invensys_equipment_name: { type: "string" },
                                invensys_point_name: { type: "string" },
                                global: {type: "boolean"}
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                },
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {field:"invensys_site_name",title:"Invensys Site Name"},
                    {field:"invensys_equipment_name",title:"Invensys Equipment Name"},
                    {field:"invensys_point_name", title:"Invensys Point Name"},
                    {
                        command:
                        [{
                            name: "Map",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                if (!dataItem.global) {
                                    equipmentDashboardPointManagementService.launchGlobalPointConfirmation(dataItem, function(returnDataItem){
                                        dataItem = returnDataItem;
                                        $scope.mapPointToInvensys(dataItem);
                                    });
                                } else {
                                    $scope.$apply(function() {
                                        $scope.mapPointToInvensys(dataItem);
                                    });
                                }
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.siemensUnknownGridOptions = {
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/data_mapping/unknownSiemens",
                            dataType: "json",
                            contentType: "application/json",
                            type: "GET"
                        },
                        parameterMap: function (options, operation) {
                            if (operation == "read")
                                return options;
                            if (operation == "create") {
                                delete options.id;
                            }
                            return kendo.stringify(options);
                        }
                    },
                    schema: {
                        data: "data",
                        total: "total",
                        model: {
                            id: "id",
                            fields: {
                                siemens_meter_name: { type: "string"},
                                global: {type: "boolean"}
                            }
                        }
                    },
                    pageSize: 10,
                    serverPaging: true
                },
                scrollable: false,
                filterable: true,
                sortable: false,
                pageable: true,
                columns: [
                    {field:"siemens_meter_name",title:"Siemens Meter Name"},
                    {
                        command:
                        [{
                            name: "Map",
                            click: function(e) {
                                var dataItem = $(e.currentTarget).closest("[kendo-grid]").data("kendoGrid").dataItem($(e.currentTarget).closest("tr"));
                                if (!dataItem.global) {
                                    equipmentDashboardPointManagementService.launchGlobalPointConfirmation(dataItem, function(returnDataItem){
                                        dataItem = returnDataItem;
                                        $scope.mapPointToSiemens(dataItem);
                                    });
                                } else {
                                    $scope.$apply(function() {
                                        $scope.mapPointToSiemens(dataItem);
                                    });
                                }
                                return false;
                            }
                        }]
                    }
                ]
            };

            $scope.refreshNumericPoints = function() {
                equipmentService.getEquipmentPoints({equipment_id: $scope.equipmentId}, function(results) {
                    $scope.numericPoints = results.data.filter(function(p) {return p["point_type"] == "NP";});
                    kendo.ui.progress($(".pat-container"), false);
                });
            };

        }
    ]);

var PreviewModalCtrl = ["$scope", "$modalInstance", "content", function ($scope, $modalInstance, content) {
    $scope.content = content;

    $scope.ok = function () {
        $modalInstance.dismiss('cancel');
    };
}];

var AddParagraphModalCtrl = ["$scope", "$modalInstance", "componentService", "categories", "type", "component_id", function($scope, $modalInstance, componentService, categories, type, component_id) {
    $scope.data = {
        categories: categories,
        paragraphs: [],
        selectedCategory: null,
        selectedParagraph: null
    };

    $scope.categoryChanged = function() {
        kendo.ui.progress($(".modal-content"), true);
        $scope.data.paragraphs.length = 0;
        $scope.data.selectedParagraph = null;

        componentService.getAvailableParagraphsByTypeAndCategory({component_id: component_id, paragraph_type: type, category_id: $scope.data.selectedCategory.id}, function(response) {
            _.each(response.results, function(paragraph) {
                $scope.data.paragraphs.push(paragraph);
            });
        }).$promise.finally(function() {
            kendo.ui.progress($(".modal-content"), false);
        });
    };

    $scope.ok = function () {
        $modalInstance.close($scope.data.selectedParagraph.id);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}];

var EditModalCtrl = ["$scope", "$modalInstance", "title", "content", function ($scope, $modalInstance, title, content) {
    $scope.data = {title: title, content: content};

    $scope.ok = function () {
        $modalInstance.close({title: $scope.data.title, content: $scope.data.content});
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}];

var RafModalCtrl = ["$scope", "$modalInstance", function ($scope, $modalInstance) {
    $scope.data = {
        name: "",
        inlet_pressure: 0, 
        discharge_pressure: 0, 
        delta_p: 0, 
        mixing_box_pressure: 0
    };
  
    $scope.ok = function () {
        $modalInstance.close($scope.data);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
}];