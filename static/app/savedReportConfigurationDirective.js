/**
 * Created by badams on 9/17/2014.
 */

angular.module('pathianApp.directives')
    .directive('savedReportConfiguration', ["$compile", "savedReportConfigurationService", "reportConfigurationSaveService",
        function ($compile, savedReportConfigurationService, reportConfigurationSaveService) {
            return {
                scope: {
                    reportType: "@",
                    reportNodes: "=",
                    reportModel: "=",
                    selectedConfig: "="
                },
                link: function(scope, elem){
                    // save initial configuration to reset to later
                    scope.resetModel = angular.copy(scope.reportModel);

                    elem.empty();

                    savedReportConfigurationService.getSavedConfigurationsByType({type:scope.reportType}, function(data) {

                        // set up the hiding/showing of the already saved configurations on the left side of the screen.
                        scope.showConfigs = false;

                        scope.reportConfigurations = data.configs;

                        var $selectContainingDiv = $(document.createElement('div'))
                            .attr('class', 'col-md-4');

                        var $savedReportSelector = $(document.createElement('select'))
                            .attr('ng-model', 'selectedConfig')
                            .attr("ng-change", 'loadConfig(selectedConfig)')
                            .attr('ng-options', 'item.id as item.name for item in reportConfigurations')
                            .attr('ng-show', 'showConfigs == true')
                            .attr('style', 'margin-bottom:12px');
                        $savedReportSelector.append("<option value=''>None</option>");

                        $selectContainingDiv.append("<span class='fake-link' ng-hide='showConfigs == true' ng-click='showConfigs = true'>Show Saved Configurations <span class='glyphicon glyphicon-chevron-right'></span></span>");
                        $selectContainingDiv.append("<span class='fake-link' ng-show='showConfigs == true' ng-click='showConfigs = false'>Hide Saved Configurations <span class='glyphicon glyphicon-chevron-down'></span></span> ");
                        $selectContainingDiv.append('<br/>');
                        $selectContainingDiv.append($savedReportSelector);

                        elem.append($selectContainingDiv);
                        $compile($selectContainingDiv)(scope);


                        // set up loading the config when selected in the dropdown
                        scope.loadConfig = function(cfg) {
                            if (cfg) {
                                // find the configuration in the list
                                var config = $.grep(scope.reportConfigurations, function(c) {
                                    return c.id === cfg;
                                })[0];
                                if (config) {
                                    scope.reportNodes = angular.copy(config.entity_ids);
                                    scope.reportModel = angular.copy(config.configuration);
                                }
                            } else {
                                // set the default values
                                scope.reportNodes = [];
                                scope.reportModel = angular.copy(scope.resetModel);
                            }
                        };

                        // set up the saving of the current configuration on the right side of the screen
                        scope.saveConfig = function() {
                            reportConfigurationSaveService.launchConfigurationSaver(scope.reportNodes, scope.reportModel, scope.reportType, function(new_config){
                                scope.reportConfigurations.push(new_config.config);
                                scope.selectedConfig = new_config.config.id;
                            });
                        };

                        var $saveContainingDiv = $(document.createElement('div'))
                            .attr('class', 'col-md-4 col-md-offset-4');

                        $saveContainingDiv.append("<span class='fake-link' style='float:right' ng-click='saveConfig()'>Save Current Configuration</span>");

                        elem.append($saveContainingDiv);
                        $compile($saveContainingDiv)(scope);

                    });

                }
            };
        }
    ]);