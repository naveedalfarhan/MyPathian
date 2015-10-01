angular.module("pathianApp.factories")
    .factory("componentTreeFactory", ["$http", "$modal", "componentService",
        function($http, $modal, componentService) {
            return {
                add: function(node) {
                    alert(node);
                },
                addMappingChild: function(draggedNode, dropTarget, dragHint, dropHint) {
                    var destinationNode = dropTarget.closest(".k-item");
                    var dropPosition;
                    var destinationParentNode = null;
                    var sourceTree = draggedNode.closest(".k-treeview");
                    var sourceTreeview = sourceTree.data("kendoTreeView");
                    var targetTree = dropTarget.closest(".k-treeview");
                    var targetTreeview = targetTree.data("kendoTreeView");


                    // dropHint is the line that shows up if the node is inserted between two other nodes.
                    // If this is visible, then we are inserting the node as a sibling to the node we're
                    // currently hovering over. The parent will therefore be the


                    if (dropHint.css("visibility") == "visible") {
                        dropPosition = dropHint.prevAll(".k-in").length > 0 ? "after" : "before";

                        var li = destinationNode.parent().closest("li");
                        if (li.length == 0 || !$.contains(targetTree.get(0), li.get(0)))
                            destinationParentNode = null;
                        else
                            destinationParentNode = li;
                    } else if (dropTarget) {
                        dropPosition = "over";

                        // moving node to root element
                        if (!destinationNode.length) {
                            destinationNode = dropTarget.closest(".k-treeview");
                        }

                        destinationParentNode = destinationNode;
                    }


                    var valid = !dragHint.find(".k-drag-status").hasClass("k-denied") && destinationParentNode !== null;

                    var dropPrevented = !targetTreeview ? true : targetTreeview.trigger("drop", {
                        sourceNode: draggedNode,
                        destinationNode: destinationNode[0],
                        valid: valid,
                        setValid: function (newValid) { valid = newValid; },
                        dropTarget: dropTarget[0],
                        dropPosition: dropPosition
                    });

                    dropHint.remove();

                    if (!valid || dropPrevented) {
                        $(draggedNode).closest(".k-treeview").data("kendoDraggable").dropped = valid;
                        return;
                    }

                    var sourceDataItem = sourceTreeview.dataItem(draggedNode);
                    var destinationParentDataItem = targetTreeview.dataItem(destinationParentNode);


                    $("#loadingSpinner").show();


                    var parentId = destinationParentDataItem ? destinationParentDataItem.id : null;
                    var promise;
                    if (parentId === null)
                        promise = $http.post("/api/components/addMappingRoot", { childId: sourceDataItem.id })
                    else
                        promise = $http.post("/api/components/" + parentId + "/addMappingChild", { childId: sourceDataItem.id });

                    promise
                        .then(function (d) {
                            targetTreeview.append(d.data.child, destinationParentNode);

                            targetTreeview.trigger("dragend", {
                                sourceNode: draggedNode,
                                destinationNode: destinationNode[0],
                                dropPosition: dropPosition
                            });

                            // everywhere there's an instance of the parent, we need to:
                            // 1. if it is not expanded, ensure it has children
                            // 2. if it is expanded, add an instance of the child
                            // if there is an instance of the child at the root level, it
                            // needs to be removed

                            if (destinationParentDataItem) {
                                targetTree.find("li[data-uid]").each(function() {
                                    var element = $(this);
                                    var dataItem = targetTreeview.dataItem(element);
                                    if (!dataItem)
                                        return;

                                    if (dataItem.id == destinationParentDataItem.id && element.data("uid") != destinationParentNode.data("uid")) {
                                        // add dummy item so that nodes with no children will now think they have children
                                        // it gets overwritten in the load
                                        dataItem.loaded(false);
                                        var mapping_child_ids = sourceDataItem.mapping_child_ids === undefined ? [] : sourceDataItem.mapping_child_ids;
                                        targetTreeview.append({ id: sourceDataItem.id, name: sourceDataItem.name, mapping_child_ids: mapping_child_ids }, element);
                                        dataItem.load();
                                    }
                                });
                            }

                            $("#loadingSpinner").hide();
                        })["catch"](function () {
                            $("#loadingSpinner").hide();

                            var modalWindow = $modal.open({
                                templateUrl: "treeErrorModal.html",
                                controller: ["$scope",
                                    function($scope) {
                                        $scope.ok = function() {
                                            modalWindow.close();
                                        };
                                    }
                                ]
                            });
                        });
                }
            };
        }
    ]);