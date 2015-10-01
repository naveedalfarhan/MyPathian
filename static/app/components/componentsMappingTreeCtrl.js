angular.module("pathianApp.controllers")
    .controller("componentsMappingTreeCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "componentService", "componentTreeFactory",
        function ($scope, $rootScope, $location, $http, $modal, componentService, componentTreeFactory) {
            $rootScope.global.linkpath = "#/admin/components";

            $scope.userPermissions = $rootScope.global.userPermissions;

            $scope.structureTreeOptions = {
                template: "#=item.num# #=item.description#",
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

            $scope.mappingTreeOptions = {
                template: "#=item.num# #=item.description#",
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
                }
            };

            var dropHint;
            $scope.structureTreeDragOptions = {
                dragstart: function(e) {
                    dropHint = $("<div class='k-drop-hint' />")
                        .css("visibility", "hidden");
                },
                dragend: function (e) {
                    componentTreeFactory.addMappingChild($(e.currentTarget[0]), $(kendo.eventTarget(e)), this.hint, dropHint);
                    dropHint.remove();
                },
                dragcancel: function(e) {
                    dropHint.remove();
                },
                drag: function (e) {
                    var dropTarget = $(kendo.eventTarget(e));
                    var hoveredItem = dropTarget.closest(".k-top,.k-mid,.k-bot");
                    var hoveredTree = dropTarget.closest(".k-treeview");
                    var hoveredTreeObject = hoveredTree.data("kendoTreeView");

                    var draggedItem = $(e.currentTarget[0]);
                    var draggedItemTree = draggedItem.closest(".k-treeview");
                    var draggedItemTreeObject = draggedItemTree.data("kendoTreeView");

                    var statusClass = "k-denied";
                    if (hoveredItem.length && hoveredTreeObject != draggedItemTreeObject) {
                        statusClass = "k-insert-middle";

                        var itemHeight = hoveredItem.outerHeight();
                        var itemTop = kendo.getOffset(hoveredItem).top;
                        var itemContent = dropTarget.closest(".k-in");
                        var delta = itemHeight / (itemContent.length > 0 ? 4 : 2);

                        var insertOnTop = e.y.location < (itemTop + delta);
                        var insertOnBottom = (itemTop + itemHeight - delta) < e.y.location;

                        var addChild = itemContent.length && !insertOnTop && !insertOnBottom;

                        dropHint.css("visibility", addChild ? "hidden" : "visible");
                        if (addChild)
                            statusClass = "k-add";
                        else {

                            var hoveredItemPos = hoveredItem.position();
                            hoveredItemPos.top += insertOnTop ? 0 : itemHeight;

                            dropHint
                                .css(hoveredItemPos)[insertOnTop ? "prependTo" : "appendTo"](dropTarget.closest(".k-item").children("div:first"));

                            if (insertOnTop && hoveredItem.hasClass("k-top"))
                                statusClass = "k-insert-top";
                            else if (insertOnBottom && hoveredItem.hasClass("k-bot"))
                                statusClass = "k-insert-bottom";
                        }
                    } else if(hoveredTreeObject != draggedItemTreeObject && hoveredTreeObject !== null) {
                        statusClass = "k-add";
                    } else {
                        dropHint.css("visibility", "hidden");
                    }

                    var statusElement = this.hint.find(".k-drag-status")[0];
                    statusElement.className = "k-icon k-drag-status " + statusClass;
                }
            };

            $scope["delete"] = function(node, dataItem) {
                var $node = node;
                var $parentNode = $node.parent().closest(".k-item");

                var tree = $node.closest("[kendo-tree-view]");
                var treeview = tree.data("kendoTreeView");

                var sourceDataItem = treeview.dataItem($node);
                var parentDataItem = treeview.dataItem($parentNode);

                componentService.get({id: dataItem.id}).$promise
                    .then(function(retrievedComponent) {
                        var modalWindow = $modal.open({
                            templateUrl: "componentRemove.html",
                            backdrop: "static",
                            controller: ["$scope",
                                function($scope) {
                                    $scope.component = {
                                        num: retrievedComponent.num,
                                        description: retrievedComponent.description
                                    };
                                    $scope.cancel = function() {
                                        modalWindow.close();
                                    };
                                    $scope.submit = function() {
                                        var promise;
                                        if (!parentDataItem)
                                            promise = componentService.removeMappingRoot({}, {childId: sourceDataItem.id}).$promise
                                        else
                                            promise = componentService.removeMappingChild({id: parentDataItem.id}, {childId: sourceDataItem.id}).$promise

                                        promise
                                            .then(function(data) {

                                                var tree = node.closest("[kendo-tree-view]");
                                                var treeview = tree.data("kendoTreeView");
                                                treeview.remove(node);
                                                modalWindow.close();
                                            })
                                            ["catch"](function(err) {
                                                alert("An error occurred");
                                            });
                                    };
                                }
                            ]
                        });
                    });

            }
        }
    ]);