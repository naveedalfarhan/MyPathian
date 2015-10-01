angular.module("pathianApp.controllers")
    .controller("equipmentNewCtrl", ["$scope", "$rootScope", "$location", "$routeParams", "groupService", "equipmentService", "componentService", "toaster",
        function ($scope, $rootScope, $location, $routeParams, groupService, equipmentService, componentService, toaster) {
            $rootScope.global.linkpath = "#/commissioning/equipment";

            $scope.viewModel = {
                component: null,
                subcomponents: [],
                selected_point_ids: {},
                available_points: [],
                points_list: [],
                available_paragraphs: [],
                selected_paragraph_ids: {},
                paragraphs: []
            };

            $scope.viewModel.group = groupService.get({id:$routeParams["groupId"]});

            $scope.model = {};

            $scope.page = "details";

            $scope.changePage = function(page) {
                var component_ids = getComponentIds();

                if (page === "points") {
                    getPoints(component_ids);
                }

                if (page === "paragraphs") {
                    getParagraphs(component_ids);
                }

                $scope.page = page;
            }

            
            $scope.submit = function () {
                if ($scope.viewModel.group)
                    $scope.model.group_id = $scope.viewModel.group.id;

                if ($scope.viewModel.component)
                    $scope.model.component_id = $scope.viewModel.component.id;

                $scope.model.subcomponent_ids = [];
                for (var i = 0; i < $scope.viewModel.subcomponents.length; ++i)
                    $scope.model.subcomponent_ids.push($scope.viewModel.subcomponents[i].id);

                $scope.model.points = getSelectedPoints();
                $scope.model.paragraphs = getSelectedParagraphs();

                equipmentService.save($scope.model, function () {
                    toaster.pop('success', "Saved", "New equipment saved.");
                    $location.path("/commissioning/equipment");
                }, function(httpResponse){
                    toaster.pop('error', "Save Failed", httpResponse.data.Message ? httpResponse.data.Message : "An Error Occurred")
                });
            };

            $scope.$watch("viewModel.component", function() {
                var urlSuffix = $scope.viewModel.component ? "/" + $scope.viewModel.component.id : "";
                $scope.subComponentTreeOptions = {
                    template: "#=item.name#",
                    dataSource: {
                        transport: {
                            read: {
                                url: "/api/components/getMappingChildrenOf" + urlSuffix,
                                dataType: "json"
                            }
                        },
                        schema: {
                            model: {
                                id: "id",
                                hasChildren: "mapping_child_ids.length > 0"
                            }
                        }
                    },
                    checkboxes: true
                };
            });

            $scope.$watchCollection("viewModel.subcomponents", function(oldValue, newValue) {
                var changed = false;
                if (oldValue.length != newValue.length)
                    changed = true;
                else {
                    for (var i = 0; i < oldValue.length; ++i)
                        if (oldValue[i] !== newValue[i])
                            changed = true;
                }
                if (!changed)
                    return;
                $scope.viewModel.selected_point_ids = {};
                $scope.viewModel.selected_paragraph_ids = {};
            });

            $scope.viewModel.points = function() {
                $scope.viewModel.points_list.length = 0;

                var point_ids = _.pluck(getSelectedPoints(), 'id');

                var all_points = _.flatten(_.pluck($scope.viewModel.available_points, 'points'));

                for (var index in all_points) {
                    var currentPoint = all_points[index];
                    if (_.contains(point_ids, currentPoint.id)){
                        $scope.viewModel.points_list.push(currentPoint);
                    }
                }

                return $scope.viewModel.points_list;
            };

            $scope.componentTreeOptions = {
                template: "#=item.name#",
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/components/getStructureChildrenOf",
                            dataType: "json"
                        }
                    },
                    schema: {
                        model: {
                            id: "id",
                            hasChildren: "structure_child_ids.length > 0"
                        }
                    }
                }
            };

            $scope.subComponentTreeOptions = {
                template: "#=item.name#",
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/components/getMappingChildrenOf",
                            dataType: "json"
                        }
                    },
                    schema: {
                        model: {
                            id: "id",
                            hasChildren: "mapping_child_ids.length > 0"
                        }
                    }
                },
                checkboxes: true
            };

            $scope.cancel = function () {
                $location.path("/commissioning/equipment");
            };

            function getComponentIds()
            {
                var component_ids = {
                    "component_ids[0]": $scope.viewModel.component.id
                };
                for (var i = 0; i < $scope.viewModel.subcomponents.length; ++i)
                    component_ids["component_ids[" + i + "]"] = $scope.viewModel.subcomponents[i].id

                if ($scope.viewModel.component)
                    component_ids["component_ids[" + $scope.viewModel.subcomponents.length + "]"] = $scope.viewModel.component.id;

                return component_ids;
            }

            function getPoints(component_ids)
            {
                var points = componentService.getPointsByComponentIds(component_ids, function() {
                    $scope.viewModel.available_points = [];
                    if ($scope.viewModel.component) {
                        var entry = {
                            component: $scope.viewModel.component,
                            points: []
                        };
                        if (entry.component.id in points)
                            entry.points = points[entry.component.id];
                        $scope.viewModel.available_points.push(entry);
                    }
                    for (var i = 0; i < $scope.viewModel.subcomponents.length; ++i) {
                        var subComponent = {
                            component: $scope.viewModel.subcomponents[i],
                            points: []
                        };
                        if (subComponent.component.id in points) {
                            subComponent.points = points[subComponent.component.id];
                        }
                        $scope.viewModel.available_points.push(subComponent);
                    }
                });
            }

            function getParagraphs(component_ids)
            {
                var response = componentService.getAllParagraphs(component_ids, function(){
                    $scope.viewModel.available_paragraphs = [];


                    for (var index in response.components) {
                        var component = response.components[index];

                        var paragraphs = _.filter(response.paragraphs, function(paragraph){
                            return paragraph.component_id === component.id;
                        });

                        var entry = {
                            component: component,
                            paragraphs: paragraphs
                        };

                        $scope.viewModel.available_paragraphs.push(entry);
                    }
                });
            }

            function getSelectedPoints(){
                var points = []

                for (var selectedPointId in $scope.viewModel.selected_point_ids) {
                    if (!$scope.viewModel.selected_point_ids[selectedPointId])
                        continue;
                    points.push({ id: selectedPointId });
                }

                return points;
            }

            function getSelectedParagraphs(){
                var paragraphs = [];

                for (var selectedParagraphId in $scope.viewModel.selected_paragraph_ids) {
                    if (!$scope.viewModel.selected_paragraph_ids[selectedParagraphId])
                        continue;
                    paragraphs.push({ id: selectedParagraphId });
                }

                return paragraphs;
            }
        }
    ]);