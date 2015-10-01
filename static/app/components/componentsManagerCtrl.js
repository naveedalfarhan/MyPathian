angular.module("pathianApp.controllers")
    .controller("componentsManagerCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "$compile", "componentService", "componentPointService", "componentParagraphService",
        function ($scope, $rootScope, $location, $http, $modal, $compile, componentService, componentPointService, componentParagraphService) {
            $rootScope.global.linkpath = "#/admin/components";

            $scope.selectedInfo = null;

            var componentSelected = function() {
                var componentId = $scope.selectedNode.id.substr(10);
                $scope.selectedInfo = {
                    componentSelected: true,
                    selectedComponent: componentService.get({id: componentId}),
                    childComponents: componentService.getStructureChildren({id: componentId})
                }
            };

            var componentsMenuSelected = function() {
                var componentId = $scope.selectedNode.id.substr(11);

                $scope.selectedInfo = {
                    componentsMenuSelected: true,
                    selectedComponent: componentService.get({id: componentId}),
                    childComponents: componentService.getStructureChildren({id: componentId})
                }
            };

            var pointsMenuSelected = function() {
                var componentId = null;
                if ($scope.selectedNode.id.substr(7, 5) == "type:") {
                    componentId = $scope.selectedNode.id.substr(15);
                    var pointType = $scope.selectedNode.id.substr(12, 2);
                    $scope.selectedInfo = {
                        pointsSpecificMenuSelected: true,
                        selectedPointType: pointType,
                        childPoints: componentPointService.getByComponent({component_id: componentId, type: pointType})
                    };
                } else {
                    componentId = $scope.selectedNode.id.substr(7);
                    $scope.selectedInfo = {
                        pointsMenuSelected: true
                    };
                }
                $scope.selectedInfo.selectedComponent = componentService.get({id: componentId});
            };

            var engineeringMenuSelected = function() {
                var componentId = null;
                if ($scope.selectedNode.id.substr(12, 5) == "type:") {
                    componentId = $scope.selectedNode.id.substr(20);
                    var engineeringType = $scope.selectedNode.id.substr(17, 2);
                    $scope.selectedInfo = {
                        engineeringSpecificMenuSelected: true,
                        selectedEngineeringType: engineeringType,
                        childParagraphs: componentParagraphService.getByComponent({component_id: componentId, type: engineeringType})
                    };
                } else {
                    componentId = $scope.selectedNode.id.substr(12);
                    $scope.selectedInfo = {
                        engineeringMenuSelected: true
                    }
                }
                $scope.selectedInfo.selectedComponent = componentService.get({id: componentId});
            };

            $scope.$watch("selectedNode", function() {
                if (!$scope.selectedNode) {
                    $scope.selectedInfo = null;
                    return;
                }

                $scope.selectedInfo = {};
                if ($scope.selectedNode.id.substr(0, 11) == "components:") {
                    componentsMenuSelected();
                } else if ($scope.selectedNode.id.substr(0, 7) == "points:") {
                    pointsMenuSelected();
                } else if ($scope.selectedNode.id.substr(0, 12) == "engineering:") {
                    engineeringMenuSelected();
                } else if ($scope.selectedNode.id.substr(0, 10) == "component:") {
                    componentSelected();
                }
            });

            $scope.fileUploadOptions = {
                url: "/api/uploadComponents",
                limitConcurrentUploads: 1,
                done: function() {
                    $(arguments[0].target).data("$scope").queue.length = 0;
                    $scope.uploadResult = arguments[1].result;
                }
            };
        }
    ]);