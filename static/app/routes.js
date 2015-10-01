angular.module("pathianApp.routes")
    .config(["$routeProvider",
        function ($routeProvider) {
            console.log("config");
            $routeProvider
                .when("/login", {
                    templateUrl: "/static/app/login/login.html",
                    controller: "loginCtrl",
                    permissions: []
                })
                .when("/home", {
                    templateUrl: "/static/app/home/home.html",
                    controller: "homeCtrl",
                    permissions: []
                })
                .when("/home/notifications", {
                    templateUrl: "/static/app/home/notifications.html",
                    controller: "notificationsCtrl",
                    permissions: []
                })
                .when("/forbidden", {
                    templateUrl: "/static/app/forbidden.html",
                    permissions: []
                })



                // users

                .when("/admin/users", {
                    templateUrl: "/static/app/users/list.html",
                    controller: "usersListCtrl",
                    permissions: ["View Users", "Manage Users"]
                })
                .when("/admin/users/:id/edit", {
                    templateUrl: "/static/app/users/edit.html",
                    controller: "usersEditCtrl",
                    permissions: ["Manage Users"]
                })
                .when("/admin/users/:id/delete", {
                    templateUrl: "/static/app/users/delete.html",
                    controller: "usersDeleteCtrl",
                    permissions: ["Manage Users"]
                })
                .when("/admin/users/new", {
                    templateUrl: "/static/app/users/new.html",
                    controller: "usersNewCtrl",
                    permissions: ["Manage Users"]
                })





                // groups

                .when("/admin/groups", {
                    templateUrl: "/static/app/groups/list.html",
                    controller: "groupsListCtrl",
                    permissions: ["View Groups", "Manage Groups"]
                })
                .when("/admin/groups/tree", {
                    templateUrl: "/static/app/groups/tree.html",
                    controller: "groupsTreeCtrl",
                    permissions: ["Manage Groups"]
                })
                .when("/admin/groups/accounts", {
                    templateUrl: "/static/app/groups/accountManager.html",
                    controller: "groupsAccountManagerCtrl",
                    permissions: ["Manage Groups"]
                })
                .when("/admin/groups/new", {
                    templateUrl: "/static/app/groups/new.html",
                    controller: "groupsNewCtrl",
                    permissions: ["Manage Groups"]
                })
                .when("/admin/groups/:id/edit", {
                    templateUrl: "/static/app/groups/edit.html",
                    controller: "groupsEditCtrl",
                    permissions: ["Manage Groups"]
                })
                .when("/admin/groups/:id/delete", {
                    templateUrl: "/static/app/groups/delete.html",
                    controller: "groupsDeleteCtrl",
                    permissions: ["Manage Groups"]
                })





                // weatherstations

                .when("/admin/weatherstations", {
                    templateUrl: "/static/app/weatherstations/list.html",
                    controller: "weatherstationsListCtrl",
                    permissions: ["View Weather Stations", "Manage Weather Stations"]
                })
                .when("/admin/weatherstations/new", {
                    templateUrl: "/static/app/weatherstations/new.html",
                    controller: "weatherstationsNewCtrl",
                    permissions: ["Manage Weather Stations"]
                })
                .when("/admin/weatherstations/:id/edit", {
                    templateUrl: "/static/app/weatherstations/edit.html",
                    controller: "weatherstationsEditCtrl",
                    permissions: ["Manage Weather Stations"]
                })
                .when("/admin/weatherstations/:id/delete", {
                    templateUrl: "/static/app/weatherstations/delete.html",
                    controller: "weatherstationsDeleteCtrl",
                    permissions: ["Manage Weather Stations"]
                })



                // equipment

                .when("/commissioning/equipment", {
                    templateUrl: "/static/app/equipment/list.html",
                    controller: "equipmentListCtrl",
                    permissions: ["Manage Equipment", "View Equipment"]
                })
                .when("/commissioning/equipment/new/:groupId", {
                    templateUrl: "/static/app/equipment/new.html",
                    controller: "equipmentNewCtrl",
                    permissions: ["Manage Equipment"]
                })
                .when("/commissioning/equipment/:id/edit", {
                    templateUrl: "/static/app/equipment/edit.html",
                    controller: "equipmentEditCtrl",
                    permissions: ["Manage Equipment"]
                })
                .when("/commissioning/equipment/:id/delete", {
                    templateUrl: "/static/app/equipment/delete.html",
                    controller: "equipmentDeleteCtrl",
                    permissions: ["Manage Equipment"]
                })
                .when("/commissioning/equipment/:id/dashboard", {
                    templateUrl: "/static/app/equipment/dashboard.html",
                    controller: "equipmentDashboardCtrl",
                    permissions: ["Manage Equipment"]
                })





                // roles

                .when("/admin/roles", {
                    templateUrl: "/static/app/roles/list.html",
                    controller: "rolesListCtrl",
                    permissions: ["View Roles", "Manage Roles"]
                })
                .when("/admin/roles/new", {
                    templateUrl: "/static/app/roles/new.html",
                    controller: "rolesNewCtrl",
                    permissions: ["Manage Roles"]
                })
                .when("/admin/roles/:id/edit", {
                    templateUrl: "/static/app/roles/edit.html",
                    controller: "rolesEditCtrl",
                    permissions: ["Manage Roles"]
                })
                .when("/admin/roles/:id/delete", {
                    templateUrl: "/static/app/roles/delete.html",
                    controller: "rolesDeleteCtrl",
                    permissions: ["Manage Roles"]
                })





                // components

                .when("/admin/components", {
                    templateUrl: "/static/app/components/main.html",
                    controller: "componentsMainCtrl",
                    permissions: ['View Component Structure Tree', 'Manage Component Structure Tree',
                                    'View Component Mapping Tree', 'Manage Component Mapping Tree',
                                    'View Component Points', 'Manage Component Points',
                                    'View Component Engineering', 'Manage Component Engineering']
                })
                .when("/admin/components/structure", {
                    templateUrl: "/static/app/components/structureTree.html",
                    controller: "componentsStructureTreeCtrl",
                    permissions: ['View Component Structure Tree', 'Manage Component Structure Tree']
                })
                .when("/admin/components/mapping", {
                    templateUrl: "/static/app/components/mappingTree.html",
                    controller: "componentsMappingTreeCtrl",
                    permissions: ['View Component Mapping Tree', 'Manage Component Mapping Tree']
                })
                .when("/admin/components/engineering", {
                    templateUrl: "/static/app/components/engineeringManager.html",
                    controller: "componentsEngineeringManagerCtrl",
                    permissions: ['View Component Engineering', 'Manage Component Engineering']
                })
                .when("/admin/components/manager", {
                    templateUrl: "/static/app/components/manager.html",
                    controller: "componentsManagerCtrl",
                    permissions: []
                })
                .when("/admin/components/upload", {
                    templateUrl: "/static/app/components/upload.html",
                    controller: "componentsUploadCtrl",
                    permissions: []
                })
                .when("/point_reporting/equipment_point_record_browser", {
                    templateUrl: "/static/app/point_data_browser/equipmentPointRecordBrowser.html",
                    controller: "equipmentPointRecordBrowserCtrl",
                    permissions: ['Run Point Data Report']
                })
                .when("/point_reporting/vendor_point_record_browser", {
                    templateUrl: "/static/app/point_data_browser/vendorPointRecordBrowser.html",
                    controller: "vendorPointRecordBrowserCtrl",
                    permissions: ['Run Point Data Report']
                })



                //syrx categoreis
                .when("/admin/syrxcategories",{
                    templateUrl: "/static/app/syrxcategories/list.html",
                    controller: "syrxCategoriesListCtrl",
                    permissions: ['Manage Categories', 'View Categories']
                })
                .when("/admin/syrxcategories/new", {
                    templateUrl: "/static/app/syrxcategories/new.html",
                    controller: "syrxCategoriesNewCtrl",
                    permissions: ['Manage Categories']
                })
                .when("/admin/syrxcategories/:id/edit", {
                    templateUrl: "/static/app/syrxcategories/edit.html",
                    controller: "syrxCategoriesEditCtrl",
                    permissions: ['Manage Categories']
                })
                .when("/admin/syrxcategories/:id/delete", {
                    templateUrl: "/static/app/syrxcategories/delete.html",
                    controller: "syrxCategoriesDeleteCtrl",
                    permissions: ["Manage Categories"]
                })

                //reset schedules
                .when("/admin/resetschedules", {
                    templateUrl: "/static/app/reset_schedules/resetSchedules.html",
                    controller: "resetSchedulesCtrl",
                    permissions: ["Manage Reset Schedules"],
                    resolve: {
                        initialData: ["resetScheduleData", function(resetScheduleData) {
                            return resetScheduleData();
                        }]
                    }
                })




                // categories

                .when("/commissioning/categories",{
                    templateUrl:"/static/app/categories/list.html",
                    controller: "categoriesListCtrl",
                    permissions: ['Manage Categories', 'View Categories']
                })
                .when("/commissioning/categories/new", {
                    templateUrl:"/static/app/categories/new.html",
                    controller:"categoriesNewCtrl",
                    permissions: ['Manage Categories']
                })
                .when("/commissioning/categories/:id/edit", {
                    templateUrl: "/static/app/categories/edit.html",
                    controller: "categoriesEditCtrl",
                    permissions: ['Manage Categories']
                })
                .when("/commissioning/categories/:id/delete", {
                    templateUrl: "/static/app/categories/delete.html",
                    controller: "categoriesDeleteCtrl",
                    permissions: ["Manage Categories"]
                })





                // contacts

                .when("/commissioning/contacts", {
                    templateUrl: "/static/app/contacts/list.html",
                    controller: "contactsListCtrl",
                    permissions: ['Manage Contacts', 'View Contacts']
                })
                .when("/commissioning/contacts/new", {
                    templateUrl: "/static/app/contacts/new.html",
                    controller: "contactsNewCtrl",
                    permissions: ["Manage Contacts"]
                })
                .when("/commissioning/contacts/:id/edit", {
                    templateUrl: "/static/app/contacts/edit.html",
                    controller: "contactsEditCtrl",
                    permissions: ['Manage Contacts']
                })
                .when("/commissioning/contacts/:id/delete", {
                    templateUrl: "/static/app/contacts/delete.html",
                    controller: "contactsDeleteCtrl",
                    permissions: ['Manage Contacts']
                })





                // tasks

                .when("/commissioning/tasks", {
                    templateUrl: "/static/app/tasks/list.html",
                    controller: "tasksListCtrl",
                    permissions: ['Manage Tasks', 'View Tasks']
                })
                .when("/commissioning/tasks/new", {
                    templateUrl: "/static/app/tasks/new.html",
                    controller: "tasksNewCtrl",
                    permissions: ['Manage Tasks']
                })
                .when("/commissioning/tasks/:id/delete", {
                    templateUrl: "/static/app/tasks/delete.html",
                    controller: "tasksDeleteCtrl",
                    permissions: ['Manage Tasks']
                })
                .when("/commissioning/tasks/:id/edit", {
                    templateUrl: "/static/app/tasks/edit.html",
                    controller: "tasksEditCtrl",
                    permissions: ['Manage Tasks']
                })





                // issues

                .when("/commissioning/issues", {
                    templateUrl:"/static/app/issues/list.html",
                    controller:"issuesListCtrl",
                    permissions: ['Manage Issues', 'View Issues']
                })
                .when("/commissioning/issues/new", {
                    templateUrl:"/static/app/issues/new.html",
                    controller:"issuesNewCtrl",
                    permissions: ['Manage Issues']
                })
                .when("/commissioning/issues/:id/edit", {
                    templateUrl: "/static/app/issues/edit.html",
                    controller:"issuesEditCtrl",
                    permissions: ['Manage Issues']
                })
                .when("/commissioning/issues/:id/delete", {
                    templateUrl: "/static/app/issues/delete.html",
                    controller: "issuesDeleteCtrl",
                    permissions: ['Manage Issues']
                })





                // projects

                .when("/commissioning/projects", {
                    templateUrl: "/static/app/projects/list.html",
                    controller: "projectsListCtrl",
                    permissions: ['Manage Projects', 'View Projects']
                })
                .when("/commissioning/projects/new", {
                    templateUrl: "/static/app/projects/new.html",
                    controller: "projectsNewCtrl",
                    permissions: ['Manage Projects']
                })
                .when("/commissioning/projects/:id/edit", {
                    templateUrl: "/static/app/projects/edit.html",
                    controller: "projectsEditCtrl",
                    permissions: ['Manage Projects']
                })
                .when("/commissioning/projects/:id/delete", {
                    templateUrl: "/static/app/projects/delete.html",
                    controller: "projectsDeleteCtrl",
                    permissions: ['Manage Projects']
                })





                // eco

                .when("/commissioning/eco", {
                    templateUrl: "/static/app/eco/list.html",
                    controller: "ecoListCtrl",
                    permissions: ['Manage ECO', 'View ECO']
                })
                .when("/commissioning/eco/new", {
                    templateUrl: "/static/app/eco/new.html",
                    controller: "ecoNewCtrl",
                    permissions: ['Manage ECO']
                })
                .when("/commissioning/eco/:id/edit", {
                    templateUrl: "/static/app/eco/edit.html",
                    controller: "ecoEditCtrl",
                    permissions: ['Manage ECO']
                })
                .when("/commissioning/eco/:id/delete", {
                    templateUrl: "/static/app/eco/delete.html",
                    controller: "ecoDeleteCtrl",
                    permissions: ['Manage ECO']
                })





                // committees

                .when("/commissioning/committees", {
                    templateUrl: "/static/app/committees/list.html",
                    controller: "committeesListCtrl",
                    permissions: ['Manage Committees', 'View Committees']
                })
                .when("/commissioning/committees/new", {
                    templateUrl: "/static/app/committees/new.html",
                    controller: "committeesNewCtrl",
                    permissions: ['Manage Committees']
                })
                .when("/commissioning/committees/:id/edit", {
                    templateUrl: "/static/app/committees/edit.html",
                    controller: "committeesEditCtrl",
                    permissions: ['Manage Committees']
                })
                .when("/commissioning/committees/:id/delete", {
                    templateUrl: "/static/app/committees/delete.html",
                    controller: "committeesDeleteCtrl",
                    permissions: ['Manage Committees']
                })





                // meetings

                .when("/commissioning/meetings", {
                    templateUrl: "/static/app/meetings/list.html",
                    controller: "meetingsListCtrl",
                    permissions: ['Manage Meetings', 'View Meetings']
                })
                .when("/commissioning/meetings/new", {
                    templateUrl: "/static/app/meetings/new.html",
                    controller: "meetingsNewCtrl",
                    permissions: ['Manage Meetings']
                })
                .when("/commissioning/meetings/:id/edit", {
                    templateUrl: "/static/app/meetings/edit.html",
                    controller: "meetingsEditCtrl",
                    permissions: ['Manage Meetings']
                })
                .when("/commissioning/meetings/:id/delete", {
                    templateUrl: "/static/app/meetings/delete.html",
                    controller: "meetingsDeleteCtrl",
                    permissions: ['Manage Meetings']
                })



                // meetingtypes

                .when("/admin/meetingtypes", {
                    templateUrl: "/static/app/meetingtypes/list.html",
                    controller: "meetingtypesListCtrl",
                    permissions: ["View Meeting Types", "Manage Meeting Types"]
                })
                .when("/admin/meetingtypes/new", {
                    templateUrl: "/static/app/meetingtypes/new.html",
                    controller: "meetingtypesNewCtrl",
                    permissions: ["Manage Meeting Types"]
                })
                .when("/admin/meetingtypes/:id/edit", {
                    templateUrl: "/static/app/meetingtypes/edit.html",
                    controller: "meetingtypesEditCtrl",
                    permissions: ["Manage Meeting Types"]
                })
                .when("/admin/meetingtypes/:id/delete", {
                    templateUrl: "/static/app/meetingtypes/delete.html",
                    controller: "meetingtypesDeleteCtrl",
                    permissions: ["Manage Meeting Types"]
                })



                // utilitycompanies

                .when("/admin/utilitycompanies", {
                    templateUrl: "/static/app/utilitycompanies/list.html",
                    controller: "utilitycompaniesListCtrl",
                    permissions: ["Manage Utility Companies", "View Utility Companies"]
                })
                .when("/admin/utilitycompanies/new", {
                    templateUrl: "/static/app/utilitycompanies/new.html",
                    controller: "utilitycompaniesNewCtrl",
                    permissions: ["Manage Utility Companies"]
                })
                .when("/admin/utilitycompanies/:id/edit", {
                    templateUrl: "/static/app/utilitycompanies/edit.html",
                    controller: "utilitycompaniesEditCtrl",
                    permissions: ["Manage Utility Companies"]
                })
                .when("/admin/utilitycompanies/:id/delete", {
                    templateUrl: "/static/app/utilitycompanies/delete.html",
                    controller: "utilitycompaniesDeleteCtrl",
                    permissions: ["Manage Utility Companies"]
                })


                // taskpriorities

                .when("/admin/taskpriorities", {
                    templateUrl: "/static/app/taskpriorities/list.html",
                    controller: "taskprioritiesListCtrl",
                    permissions: ["View Task Priorities", "Manage Task Priorities"]
                })
                .when("/admin/taskpriorities/new", {
                    templateUrl: "/static/app/taskpriorities/new.html",
                    controller: "taskprioritiesNewCtrl",
                    permissions: ["Manage Task Priorities"]
                })
                .when("/admin/taskpriorities/:id/edit", {
                    templateUrl: "/static/app/taskpriorities/edit.html",
                    controller: "taskprioritiesEditCtrl",
                    permissions: ["Manage Task Priorities"]
                })
                .when("/admin/taskpriorities/:id/delete", {
                    templateUrl: "/static/app/taskpriorities/delete.html",
                    controller: "taskprioritiesDeleteCtrl",
                    permissions: ["Manage Task Priorities"]
                })

                // taskstatuses

                .when("/admin/taskstatuses", {
                    templateUrl: "/static/app/taskstatuses/list.html",
                    controller: "taskstatusesListCtrl",
                    permissions: ["Manage Task Statuses", "View Task Statuses"]
                })
                .when("/admin/taskstatuses/new", {
                    templateUrl: "/static/app/taskstatuses/new.html",
                    controller: "taskstatusesNewCtrl",
                    permissions: ["Manage Task Statuses"]
                })
                .when("/admin/taskstatuses/:id/edit", {
                    templateUrl: "/static/app/taskstatuses/edit.html",
                    controller: "taskstatusesEditCtrl",
                    permissions: ["Manage Task Statuses"]
                })
                .when("/admin/taskstatuses/:id/delete", {
                    templateUrl: "/static/app/taskstatuses/delete.html",
                    controller: "taskstatusesDeleteCtrl",
                    permissions: ["Manage Task Statuses"]
                })

                // tasktypes

                .when("/admin/tasktypes", {
                    templateUrl: "/static/app/tasktypes/list.html",
                    controller: "tasktypesListCtrl",
                    permissions: ["Manage Task Types", "View Task Types"]
                })
                .when("/admin/tasktypes/new", {
                    templateUrl: "/static/app/tasktypes/new.html",
                    controller: "tasktypesNewCtrl",
                    permissions: ["Manage Task Types"]
                })
                .when("/admin/tasktypes/:id/edit", {
                    templateUrl: "/static/app/tasktypes/edit.html",
                    controller: "tasktypesEditCtrl",
                    permissions: ["Manage Task Types"]
                })
                .when("/admin/tasktypes/:id/delete", {
                    templateUrl: "/static/app/tasktypes/delete.html",
                    controller: "tasktypesDeleteCtrl",
                    permissions: ["Manage Task Types"]
                })


                // issuepriorities

                .when("/admin/issuepriorities", {
                    templateUrl: "/static/app/issuepriorities/list.html",
                    controller: "issueprioritiesListCtrl",
                    permissions: ["Manage Issue Priorities", "View Issue Priorities"]
                })
                .when("/admin/issuepriorities/new", {
                    templateUrl: "/static/app/issuepriorities/new.html",
                    controller: "issueprioritiesNewCtrl",
                    permissions: ["Manage Issue Priorities"]
                })
                .when("/admin/issuepriorities/:id/edit", {
                    templateUrl: "/static/app/issuepriorities/edit.html",
                    controller: "issueprioritiesEditCtrl",
                    permissions: ["Manage Issue Priorities"]
                })
                .when("/admin/issuepriorities/:id/delete", {
                    templateUrl: "/static/app/issuepriorities/delete.html",
                    controller: "issueprioritiesDeleteCtrl",
                    permissions: ["Manage Issue Priorities"]
                })

                // issuestatuses

                .when("/admin/issuestatuses", {
                    templateUrl: "/static/app/issuestatuses/list.html",
                    controller: "issuestatusesListCtrl",
                    permissions: ["Manage Issue Statuses", "View Issue Statuses"]
                })
                .when("/admin/issuestatuses/new", {
                    templateUrl: "/static/app/issuestatuses/new.html",
                    controller: "issuestatusesNewCtrl",
                    permissions: ["Manage Issue Statuses"]
                })
                .when("/admin/issuestatuses/:id/edit", {
                    templateUrl: "/static/app/issuestatuses/edit.html",
                    controller: "issuestatusesEditCtrl",
                    permissions: ["Manage Issue Statuses"]
                })
                .when("/admin/issuestatuses/:id/delete", {
                    templateUrl: "/static/app/issuestatuses/delete.html",
                    controller: "issuestatusesDeleteCtrl",
                    permissions: ["Manage Issue Statuses"]
                })

                // issuetypes

                .when("/admin/issuetypes", {
                    templateUrl: "/static/app/issuetypes/list.html",
                    controller: "issuetypesListCtrl",
                    permissions: ["Manage Issue Types", "View Issue Types"]
                })
                .when("/admin/issuetypes/new", {
                    templateUrl: "/static/app/issuetypes/new.html",
                    controller: "issuetypesNewCtrl",
                    permissions: ["Manage Issue Types"]
                })
                .when("/admin/issuetypes/:id/edit", {
                    templateUrl: "/static/app/issuetypes/edit.html",
                    controller: "issuetypesEditCtrl",
                    permissions: ["Manage Issue Types"]
                })
                .when("/admin/issuetypes/:id/delete", {
                    templateUrl: "/static/app/issuetypes/delete.html",
                    controller: "issuetypesDeleteCtrl",
                    permissions: ["Manage Issue Types"]
                })

                // actionitempriorities

                .when("/admin/actionitempriorities", {
                    templateUrl: "/static/app/actionitempriorities/list.html",
                    controller: "actionitemprioritiesListCtrl",
                    permissions: ["Manage Action Item Priorities", "View Action Item Priorities"]
                })
                .when("/admin/actionitempriorities/new", {
                    templateUrl: "/static/app/actionitempriorities/new.html",
                    controller: "actionitemprioritiesNewCtrl",
                    permissions: ["Manage Action Item Priorities"]
                })
                .when("/admin/actionitempriorities/:id/edit", {
                    templateUrl: "/static/app/actionitempriorities/edit.html",
                    controller: "actionitemprioritiesEditCtrl",
                    permissions: ["Manage Action Item Priorities"]
                })
                .when("/admin/actionitempriorities/:id/delete", {
                    templateUrl: "/static/app/actionitempriorities/delete.html",
                    controller: "actionitemprioritiesDeleteCtrl",
                    permissions: ["Manage Action Item Priorities"]
                })

                // actionitemstatuses

                .when("/admin/actionitemstatuses", {
                    templateUrl: "/static/app/actionitemstatuses/list.html",
                    controller: "actionitemstatusesListCtrl",
                    permissions: ["Manage Action Item Statuses", "View Action Item Statuses"]
                })
                .when("/admin/actionitemstatuses/new", {
                    templateUrl: "/static/app/actionitemstatuses/new.html",
                    controller: "actionitemstatusesNewCtrl",
                    permissions: ["Manage Action Item Statuses"]
                })
                .when("/admin/actionitemstatuses/:id/edit", {
                    templateUrl: "/static/app/actionitemstatuses/edit.html",
                    controller: "actionitemstatusesEditCtrl",
                    permissions: ["Manage Action Item Statuses"]
                })
                .when("/admin/actionitemstatuses/:id/delete", {
                    templateUrl: "/static/app/actionitemstatuses/delete.html",
                    controller: "actionitemstatusesDeleteCtrl",
                    permissions: ["Manage Action Item Statuses"]
                })
                
                // actionitemtypes

                .when("/admin/actionitemtypes", {
                    templateUrl: "/static/app/actionitemtypes/list.html",
                    controller: "actionitemtypesListCtrl",
                    permissions: ["Manage Action Item Types", "View Action Item Types"]
                })
                .when("/admin/actionitemtypes/new", {
                    templateUrl: "/static/app/actionitemtypes/new.html",
                    controller: "actionitemtypesNewCtrl",
                    permissions: ["Manage Action Item Types"]
                })
                .when("/admin/actionitemtypes/:id/edit", {
                    templateUrl: "/static/app/actionitemtypes/edit.html",
                    controller: "actionitemtypesEditCtrl",
                    permissions: ["Manage Action Item Types"]
                })
                .when("/admin/actionitemtypes/:id/delete", {
                    templateUrl: "/static/app/actionitemtypes/delete.html",
                    controller: "actionitemtypesDeleteCtrl",
                    permissions: ["Manage Action Item Types"]
                })

                // contracts

                .when("/admin/contracts", {
                    templateUrl: "/static/app/contracts/list.html",
                    controller: "contractsListCtrl",
                    permissions: []
                })
                .when("/admin/contracts/new", {
                    templateUrl: "/static/app/contracts/new.html",
                    controller: "contractsNewCtrl",
                    permissions: []
                })
                .when("/admin/contracts/:id/edit", {
                    templateUrl: "/static/app/contracts/edit.html",
                    controller: "contractsEditCtrl",
                    permissions: []
                })
                .when("/admin/contracts/:id/delete", {
                    templateUrl: "/static/app/contracts/delete.html",
                    controller: "contractsDeleteCtrl",
                    permissions: []
                })
                // reporting

                .when("/reporting/uploadGroupData", {
                    templateUrl: "/static/app/upload/group.html",
                    controller: "uploadGroupDataCtrl",
                    permissions: ['Upload Group Data']
                })

                .when("/reporting/uploadProgress", {
                    templateUrl: "/static/app/upload/progress.html",
                    controller: "uploadProgressCtrl",
                    permissions: []
                })

                .when("/reporting/uploadTest", {
                    templateUrl: "/static/app/upload/test.html",
                    controller: "uploadTestCtrl",
                    permissions: []
                })

                // reporting groups
                .when("/reporting/groups", {
                    templateUrl:"/static/app/reporting_groups/main.html",
                    controller: "reportingGroupsMainCtrl",
                    permissions: ['Run Group Reports']
                })

                // reporting naics
                .when("/reporting/naics", {
                    templateUrl:"/static/app/reporting_naics/main.html",
                    controller:"reportingNaicsMainCtrl",
                    permissions: ['Run NAICS Reports']
                })

                // reporting sic
                .when("/reporting/sic", {
                    templateUrl:"/static/app/reporting_sic/main.html",
                    controller:"reportingSicMainCtrl",
                    permissions: ['Run SIC Reports']
                })

                // reporting equipment
                .when("/reporting/equipment", {
                    templateUrl:"/static/app/reporting_equipment_syrx/main.html",
                    controller:"reportingEquipmentSyrxCtrl",
                    permissions: ['Run Equipment Syrx Reports']
                })

                // reporting components
                .when("/reporting/components/standards", {
                    templateUrl:"/static/app/reporting_components/standards_comparison.html",
                    controller:"reportingComponentsStandardsCtrl",
                    permissions: ['Run Component Reports']
                })
                .when("/reporting/components/comparisons", {
                    templateUrl: "/static/app/reporting_components/component_comparison.html",
                    controller: "reportingComponentsComparisonCtrl",
                    permissions: ["Run Component Reports"]
                })
                .when("/reporting/components/difference", {
                    templateUrl:"/static/app/reporting_components/component_difference.html",
                    controller: "reportingComponentsDifferenceCtrl",
                    permissions: ["Run Component Reports"]
                })

                // reporting accounts
                .when("/reporting/accounts/viewData", {
                    templateUrl: "/static/app/reporting_accounts/viewData.html",
                    controller: "viewDataCtrl",
                    permissions: ["View Reporting Data"]
                })

                .when("/bronze", {
                    templateUrl: "/static/app/bronze_reporting/index.html",
                    controller: "bronzeReportingIndexCtrl",
                    permissions: []
                })
                .when("/bronze/start", {
                    templateUrl: "/static/app/bronze_reporting/start.html",
                    controller: "bronzeReportingStartCtrl",
                    permissions: []
                })
                .when("/bronze/upload/:accountType", {
                    templateUrl: "/static/app/bronze_reporting/upload.html",
                    controller: "bronzeReportingUploadCtrl",
                    permissions: []
                })
                .when("/bronze/upload", {
                    templateUrl: "/static/app/bronze_reporting/accountDetails.html",
                    controller: "bronzeReportingAccountDetailsCtrl",
                    permissions: []
                })
                .when("/bronze/summary", {
                    templateUrl: "/static/app/bronze_reporting/summary.html",
                    controller: "bronzeReportingSummaryCtrl",
                    permissions: []
                })
                .when("/admin/bronze", {
                    templateUrl: "/static/app/bronze_reporting_admin/list.html",
                    controller: "bronzeReportingSubmissionsListCtrl",
                    permissions: ['Run Bronze Reports']
                })
                .when("/data_mapping/johnson", {
                    templateUrl: "/static/app/data_mapping/johnson.html",
                    controller: "dataMappingJohnsonCtrl",
                    permissions: []
                })
                .when("/data_mapping/ies", {
                    templateUrl: "/static/app/data_mapping/invensys.html",
                    controller: "dataMappingIesCtrl",
                    permissions: []
                })
                .when("/data_mapping/siemens", {
                    templateUrl: "/static/app/data_mapping/siemens.html",
                    controller: "dataMappingSiemensCtrl",
                    permissions: []
                })
                .when("/data_mapping/unknown/johnson/:siteId?", {
                    templateUrl: "/static/app/data_mapping/unknownJohnson.html",
                    controller: "unknownJohnsonCtrl",
                    permissions: []
                })

                .when("/test/datadump", {
                    templateUrl: "/static/app/test_data_dump/index.html",
                    controller: "testDataDumpCtrl"
                })

                .otherwise({
                    redirectTo: "/home"
                });
        }
    ]);