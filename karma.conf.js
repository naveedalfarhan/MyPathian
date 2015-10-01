// Karma configuration
// Generated on Tue Feb 10 2015 10:05:44 GMT-0700 (MST)

module.exports = function (config) {
    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '',


        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine'],

        // list of files / patterns to load in the browser
        // Due to time constraints I'm loading all of the files that are loaded in the browser.
        // Later, we can delete the files that aren't being used for testing.
        files: [
            "static/js/jquery-1.10.2.min.js",
            "static/js/jquery.ui.widget.js",

            "static/js/angular.min.js",
            "static/js/angular-sanitize.min.js",
            "static/js/angular-resource.min.js",
            "static/js/angular-route.min.js",
            "static/js/angular-upload.min.js",
            "static/js/angular-animate.min.js",

            "static/js/kendo.all.min.js",
            "static/js/angular-kendo.js",

            "static/js/bootstrap.js",
            "static/js/respond.js",
            "static/js/ui-bootstrap-0.10.0.js",
            "static/js/ui-bootstrap-tpls-0.10.0.js",

            "static/js/draganddrop.js",
            "static/js/ckeditor.js",
            "static/js/toaster.js",
            "static/js/underscore-min.js",

            "static/js/jquery.iframe-transport.js",
            "static/js/jquery.fileupload.js",
            "static/js/jquery.fileupload-process.js",
            "static/js/jquery.fileupload-validate.js",
            "static/js/jquery.fileupload-angular.js",

            "static/app/app.js",
            "static/app/ckEditorDirective.js",
            "static/app/fileUploadButtonDirective.js",
            "static/app/globalInterceptor.js",
            "static/app/kendoDraggableDirective.js",
            "static/app/kendoTreeViewDirective.js",
            "static/app/multiPickerDirective.js",
            "static/app/peakReportDirective.js",
            "static/app/permissionHandler.js",
            "static/app/reportingConsumptionChartDirective.js",
            "static/app/reportingIntensityChartDirective.js",
            "static/app/reportingTreeDirective.js",
            "static/app/routes.js",
            "static/app/savedReportConfigurationDirective.js",
            "static/app/services.js",
            "static/app/singlePickerDirective.js",
            "static/app/textReportDirective.js",
            "static/app/actionitempriorities/actionitemprioritiesDeleteCtrl.js",
            "static/app/actionitempriorities/actionitemprioritiesEditCtrl.js",
            "static/app/actionitempriorities/actionitemprioritiesListCtrl.js",
            "static/app/actionitempriorities/actionitemprioritiesNewCtrl.js",
            "static/app/actionitemstatuses/actionitemstatusesDeleteCtrl.js",
            "static/app/actionitemstatuses/actionitemstatusesEditCtrl.js",
            "static/app/actionitemstatuses/actionitemstatusesListCtrl.js",
            "static/app/actionitemstatuses/actionitemstatusesNewCtrl.js",
            "static/app/actionitemtypes/actionitemtypesDeleteCtrl.js",
            "static/app/actionitemtypes/actionitemtypesEditCtrl.js",
            "static/app/actionitemtypes/actionitemtypesListCtrl.js",
            "static/app/actionitemtypes/actionitemtypesNewCtrl.js",
            "static/app/bronze_reporting/bronzeReportingAccountDetailsCtrl.js",
            "static/app/bronze_reporting/bronzeReportingFormService.js",
            "static/app/bronze_reporting/bronzeReportingIndexCtrl.js",
            "static/app/bronze_reporting/bronzeReportingStartCtrl.js",
            "static/app/bronze_reporting/bronzeReportingSummaryCtrl.js",
            "static/app/bronze_reporting/bronzeReportingUploadCtrl.js",
            "static/app/bronze_reporting/manualEnergyGridDirective.js",
            "static/app/bronze_reporting_admin/bronzeReportingSubmissionsListCtrl.js",
            "static/app/categories/categoriesDeleteCtrl.js",
            "static/app/categories/categoriesEditCtrl.js",
            "static/app/categories/categoriesListCtrl.js",
            "static/app/categories/categoriesNewCtrl.js",
            "static/app/committees/committeesDeleteCtrl.js",
            "static/app/committees/committeesEditCtrl.js",
            "static/app/committees/committeesListCtrl.js",
            "static/app/committees/committeesNewCtrl.js",
            "static/app/components/componentEngineeringTableDirective.js",
            "static/app/components/componentIssueTableDirective.js",
            "static/app/components/componentManagerTreeDirective.js",
            "static/app/components/componentMappingTreeDirective.js",
            "static/app/components/componentPointTableDirective.js",
            "static/app/components/componentPointTreeDirective.js",
            "static/app/components/componentsEngineeringManagerCtrl.js",
            "static/app/components/componentsMainCtrl.js",
            "static/app/components/componentsManagerCtrl.js",
            "static/app/components/componentsMappingTreeCtrl.js",
            "static/app/components/componentsStructureTreeCtrl.js",
            "static/app/components/componentStructureTreeDirective.js",
            "static/app/components/componentsUploadCtrl.js",
            "static/app/components/componentTaskTableDirective.js",
            "static/app/components/componentTreeFactory.js",
            "static/app/contacts/contactsDeleteCtrl.js",
            "static/app/contacts/contactsEditCtrl.js",
            "static/app/contacts/contactsListCtrl.js",
            "static/app/contacts/contactsNewCtrl.js",
            "static/app/contracts/contractsDeleteCtrl.js",
            "static/app/contracts/contractsEditCtrl.js",
            "static/app/contracts/contractsListCtrl.js",
            "static/app/contracts/contractsNewCtrl.js",
            "static/app/data_mapping/dataMappingInvensysCtrl.js",
            "static/app/data_mapping/dataMappingJohnsonCtrl.js",
            "static/app/data_mapping/dataMappingSiemensCtrl.js",
            "static/app/data_mapping/unknownJohnsonCtrl.js",
            "static/app/eco/ecoDeleteCtrl.js",
            "static/app/eco/ecoEditCtrl.js",
            "static/app/eco/ecoListCtrl.js",
            "static/app/eco/ecoNewCtrl.js",
            "static/app/equipment/equipmentConsumptionTableDirective.js",
            "static/app/equipment/equipmentDashboardCtrl.js",
            "static/app/equipment/equipmentDeleteCtrl.js",
            "static/app/equipment/equipmentEditCtrl.js",
            "static/app/equipment/equipmentListCtrl.js",
            "static/app/equipment/equipmentManagerTreeDirective.js",
            "static/app/equipment/equipmentNewCtrl.js",
            "static/app/equipment/equipmentService.js",
            "static/app/equipment/equipmentTableDirective.js",
            "static/app/equipment/numericPointValueGridDirective.js",
            "static/app/groups/groupsAccountManagerCtrl.js",
            "static/app/groups/groupsEditCtrl.js",
            "static/app/groups/groupsListCtrl.js",
            "static/app/groups/groupsNewCtrl.js",
            "static/app/groups/groupsTreeCtrl.js",
            "static/app/groups/groupTreeDirective.js",
            "static/app/groups/groupTreeFactory.js",
            "static/app/home/benchmarkBudgetVarianceTableDirective.js",
            "static/app/home/benchmarkPerformanceTableDirective.js",
            "static/app/home/dashboardChartDirective.js",
            "static/app/home/dashboardTableDirective.js",
            "static/app/home/homeCtrl.js",
            "static/app/home/notificationListDirective.js",
            "static/app/home/notificationsCtrl.js",
            "static/app/issuepriorities/issueprioritiesDeleteCtrl.js",
            "static/app/issuepriorities/issueprioritiesEditCtrl.js",
            "static/app/issuepriorities/issueprioritiesListCtrl.js",
            "static/app/issuepriorities/issueprioritiesNewCtrl.js",
            "static/app/issues/issuesDeleteCtrl.js",
            "static/app/issues/issuesEditCtrl.js",
            "static/app/issues/issuesListCtrl.js",
            "static/app/issues/issuesNewCtrl.js",
            "static/app/issuestatuses/issuestatusesDeleteCtrl.js",
            "static/app/issuestatuses/issuestatusesEditCtrl.js",
            "static/app/issuestatuses/issuestatusesListCtrl.js",
            "static/app/issuestatuses/issuestatusesNewCtrl.js",
            "static/app/issuetypes/issuetypesDeleteCtrl.js",
            "static/app/issuetypes/issuetypesEditCtrl.js",
            "static/app/issuetypes/issuetypesListCtrl.js",
            "static/app/issuetypes/issuetypesNewCtrl.js",
            "static/app/login/loginCtrl.js",
            "static/app/meetings/meetingsDeleteCtrl.js",
            "static/app/meetings/meetingsEditCtrl.js",
            "static/app/meetings/meetingsListCtrl.js",
            "static/app/meetings/meetingsNewCtrl.js",
            "static/app/meetingtypes/meetingtypesDeleteCtrl.js",
            "static/app/meetingtypes/meetingtypesEditCtrl.js",
            "static/app/meetingtypes/meetingtypesListCtrl.js",
            "static/app/meetingtypes/meetingtypesNewCtrl.js",
            "static/app/projects/projectsDeleteCtrl.js",
            "static/app/projects/projectsEditCtrl.js",
            "static/app/projects/projectsListCtrl.js",
            "static/app/projects/projectsNewCtrl.js",
            "static/app/reporting_accounts/viewDataCtrl.js",
            "static/app/reporting_components/componentComparisonTableDirective.js",
            "static/app/reporting_components/componentConsumptionChartDirective.js",
            "static/app/reporting_components/componentDifferenceChartDirective.js",
            "static/app/reporting_components/componentReportingTreeDirective.js",
            "static/app/reporting_components/componentStandardsTableDirective.js",
            "static/app/reporting_components/reportingComponentsComparisonCtrl.js",
            "static/app/reporting_components/reportingComponentsDifferenceCtrl.js",
            "static/app/reporting_components/reportingComponentsStandardsCtrl.js",
            "static/app/reporting_equipment_syrx/reportingEquipmentSyrxCtrl.js",
            "static/app/reporting_groups/reportingGroupsMainCtrl.js",
            "static/app/reporting_naics/naicsReportingTreeDirective.js",
            "static/app/reporting_naics/reportingNaicsMainCtrl.js",
            "static/app/reporting_sic/reportingSicMainCtrl.js",
            "static/app/reporting_sic/sicReportingTreeDirective.js",
            "static/app/reset_schedules/resetSchedulesCtrl.js",
            "static/app/reset_schedules/resetScheduleService.js",
            "static/app/roles/rolesDeleteCtrl.js",
            "static/app/roles/rolesEditCtrl.js",
            "static/app/roles/rolesListCtrl.js",
            "static/app/roles/rolesNewCtrl.js",
            "static/app/syrxcategories/syrxCategoriesDeleteCtrl.js",
            "static/app/syrxcategories/syrxCategoriesEditCtrl.js",
            "static/app/syrxcategories/syrxCategoriesListCtrl.js",
            "static/app/syrxcategories/syrxCategoriesNewCtrl.js",
            "static/app/taskpriorities/taskprioritiesDeleteCtrl.js",
            "static/app/taskpriorities/taskprioritiesEditCtrl.js",
            "static/app/taskpriorities/taskprioritiesListCtrl.js",
            "static/app/taskpriorities/taskprioritiesNewCtrl.js",
            "static/app/tasks/tasksDeleteCtrl.js",
            "static/app/tasks/tasksEditCtrl.js",
            "static/app/tasks/tasksListCtrl.js",
            "static/app/tasks/tasksNewCtrl.js",
            "static/app/taskstatuses/taskstatusesDeleteCtrl.js",
            "static/app/taskstatuses/taskstatusesEditCtrl.js",
            "static/app/taskstatuses/taskstatusesListCtrl.js",
            "static/app/taskstatuses/taskstatusesNewCtrl.js",
            "static/app/tasktypes/tasktypesDeleteCtrl.js",
            "static/app/tasktypes/tasktypesEditCtrl.js",
            "static/app/tasktypes/tasktypesListCtrl.js",
            "static/app/tasktypes/tasktypesNewCtrl.js",
            "static/app/test_data_dump/testDataDumpCtrl.js",
            "static/app/upload/uploadGroupDataCtrl.js",
            "static/app/upload/uploadProgressCtrl.js",
            "static/app/upload/uploadTestCtrl.js",
            "static/app/users/usersDeleteCtrl.js",
            "static/app/users/usersEditCtrl.js",
            "static/app/users/usersListCtrl.js",
            "static/app/users/usersNewCtrl.js",
            "static/app/utilitycompanies/utilitycompaniesDeleteCtrl.js",
            "static/app/utilitycompanies/utilitycompaniesEditCtrl.js",
            "static/app/utilitycompanies/utilitycompaniesListCtrl.js",
            "static/app/utilitycompanies/utilitycompaniesNewCtrl.js",
            "static/app/weatherstations/weatherstationsDeleteCtrl.js",
            "static/app/weatherstations/weatherstationsEditCtrl.js",
            "static/app/weatherstations/weatherstationsListCtrl.js",
            "static/app/weatherstations/weatherstationsNewCtrl.js",

            'static/js/sinon-1.12.2.js',
            'node_modules/should/should.js',
            'static/js/angular-mocks.js',

            // Code under tests
            'static/tests/spec/**/*Spec.js'
        ],

        // list of files to exclude
        exclude: [],


        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {},


        // test results reporter to use
        // possible values: 'dots', 'progress'
        // available reporters: https://npmjs.org/browse/keyword/karma-reporter
        reporters: ['progress'],


        // web server port
        port: 9876,


        // enable / disable colors in the output (reporters and logs)
        colors: true,


        // level of logging
        // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
        logLevel: config.LOG_INFO,


        // enable / disable watching file and executing tests whenever any file changes
        autoWatch: true,


        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: ['PhantomJS'],


        // Continuous Integration mode
        // if true, Karma captures browsers, runs the tests and exits
        singleRun: false
    });
};
