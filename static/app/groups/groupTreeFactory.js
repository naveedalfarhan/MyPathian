angular.module("pathianApp.factories")
    .factory("groupTreeFactory", ["$http", "$modal", "groupService",
        function($http, $modal, groupService) {
            return {
                addChild: function(sourceNode, dropTarget, dragHint, dropHint) {
                    var destinationNode = undefined;
                    var dropPosition = "over";
                    var tree = dropTarget.closest(".k-treeview");
                    var treeview = tree.data("kendoTreeView");

                    if (dropHint.css("visibility") == "visible") {
                        dropPosition = dropHint.prevAll(".k-in").length > 0 ? "after" : "before";
                        destinationNode = dropHint.closest(".k-item");
                    } else if (dropTarget) {
                        destinationNode = dropTarget.closest(".k-item");

                        // moving node to root element
                        if (!destinationNode.length) {
                            destinationNode = dropTarget.closest(".k-treeview");
                        }
                    }


                    console.log(dropPosition);
                    console.log(destinationNode);

                    var parent = null;
                    if (dropPosition == "over")
                        parent = destinationNode;
                    else {
                        var li = destinationNode.parent().closest("li");
                        if (li.length == 0 || !$.contains(tree[0], li[0]))
                            parent = null;
                        else
                            parent = li;
                    }

                    var grid = $(sourceNode).closest(".k-grid").data("kendoGrid");
                    var sourceDataItem = grid.dataItem(sourceNode);
                    var valid = !dragHint.find(".k-drag-status").hasClass("k-denied") && parent !== null;

                    var dropPrevented = !treeview ? true : treeview.trigger("drop", {
                        sourceNode: sourceDataItem,
                        destinationNode: destinationNode[0],
                        valid: valid,
                        setValid: function (newValid) { valid = newValid; },
                        dropTarget: dropTarget[0],
                        dropPosition: dropPosition
                    });

                    dropHint.remove();

                    if (!valid || dropPrevented) {
                        return;
                    }



                    var parentDataItem = treeview.dataItem(parent);


                    $("#loadingSpinner").show();


                    if (parentDataItem === undefined) {
                        $http.post("/api/groups/addRoot", { childId: sourceDataItem.id })
                            .then(function(d) {
                                treeview.append(d.data.child, null);

                                treeview.trigger("dragend", {
                                    sourceNode: sourceNode,
                                    destinationNode: destinationNode[0],
                                    dropPosition: dropPosition
                                });$("#loadingSpinner").hide();
                            }, function () {
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
                    } else {
                        $http.post("/api/groups/" + parentDataItem.id + "/addChild", { childId: sourceDataItem.id })
                            .then(function (d) {
                                treeview.append(d.data.child, parent);

                                treeview.trigger("dragend", {
                                    sourceNode: sourceNode,
                                    destinationNode: destinationNode[0],
                                    dropPosition: dropPosition
                                });

                                // everywhere there's an instance of the parent, we need to:
                                // 1. if it is not expanded, ensure it has children
                                // 2. if it is expanded, add an instance of the child

                                tree.find("li[data-uid]").each(function() {
                                    var element = $(this);
                                    var dataItem = treeview.dataItem(element);
                                    if (!dataItem)
                                        return;

                                    if (dataItem.id == parentDataItem.id && element.data("uid") != parent.data("uid")) {
                                        // add dummy item so that nodes with no children will now think they have children
                                        // it gets overwritten in the load
                                        dataItem.loaded(false);
                                        treeview.append({ id: sourceDataItem.id, name: sourceDataItem.name, childIds: sourceDataItem.childIds }, element);
                                        dataItem.load();
                                    }
                                });


                                $("#loadingSpinner").hide();
                            }, function () {
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

                    var valid = !dragHint.find(".k-drag-status").hasClass("k-denied") && parent !== null;

                    var dropPrevented = !treeview ? true : treeview.trigger("drop", {
                        sourceNode: sourceNode,
                        destinationNode: destinationNode[0],
                        valid: valid,
                        setValid: function (newValid) { valid = newValid; },
                        dropTarget: dropTarget[0],
                        dropPosition: dropPosition
                    });

                    dropHint.remove();

                    if (!valid || dropPrevented) {
                        $(sourceNode).closest(".k-grid").data("kendoDraggable").dropped = valid;
                        return;
                    }
                },
                removeChild: function(node) {
                    var $node = node;
                    var $parentNode = $node.parent().closest(".k-item");

                    var tree = $node.closest("[kendo-tree-view]");
                    var treeview = tree.data("kendoTreeView");

                    var sourceDataItem = treeview.dataItem($node);
                    var parentDataItem = treeview.dataItem($parentNode);

                    $("#loadingSpinner").show();


                    if (parentDataItem === undefined) {
                        $http.post("/api/groups/removeRoot", { childId: sourceDataItem.id })
                            .then(function(d) {
                                treeview.remove(node);
                                $("#loadingSpinner").hide();
                            }, function () {
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
                            }, function () {
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
                    } else {
                        $http.post("/api/groups/" + parentDataItem.id + "/removeChild", { childId: sourceDataItem.id })
                            .then(function (d) {

                                // We need to remove the original child node, as well as
                                // the child node on every instance of the parent node.
                                // We go through the tree and examine every instance of the
                                // parent node -- if it hasn't been expanded yet, ignore it.
                                // Otherwise, remove the instance of the child node.
                                // Once done, make a server call to determine if the child now
                                // has no parents. If it has no parents, add it to the root level.

                                tree.find("li[data-uid]").each(function() {
                                    var element = $(this);
                                    var dataItem = treeview.dataItem(element);
                                    if (!dataItem)
                                        return;

                                    if (dataItem.id == parentDataItem.id) {
                                        element.find("li[data-uid]").each(function() {
                                            var childDataItem = treeview.dataItem($(this));
                                            if (childDataItem !== undefined && childDataItem.id == sourceDataItem.id)
                                                treeview.remove($(this));
                                        });
                                    }
                                });

                                treeview.remove(node);
                                $("#loadingSpinner").hide();
                                $("[data-name='group-tree-node-delete']").remove();

                                return groupService.get({ id: sourceDataItem.id }).$promise;
                            }, function () {
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
                }
            };
        }
    ]);