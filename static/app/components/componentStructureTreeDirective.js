angular.module("pathianApp.directives")
    .directive("componentStructureTree", ["$parse", "$timeout", "$compile", "$modal", "componentService",
        function ($parse, $timeout, $compile, $modal, componentService) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: false,
                compile: function (elem, attrs) {
                    // build the inner elements
                    var $tree;

                    if (attrs["selectionStyle"]) {
                        $tree = $(document.createElement("div"))
                            .attr("selectable-tree-view", "")
                            .attr("k-options", attrs["kOptions"])
                            .attr("ng-bind", attrs["ngBind"])
                            .attr("ng-model", attrs["ngModel"])
                            .attr("selection-style", attrs["selectionStyle"]);
                    } else {
                        $tree = $(document.createElement("div"))
                            .attr("kendo-tree-view", "")
                            .attr("k-options", attrs["kOptions"]);
                    }

                    if ("edit" in attrs)
                        $tree.attr("edit", attrs["edit"]);

                    elem.replaceWith($tree);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile

                            var gridoptions = $parse(attrs["kOptions"])(scope);

                            if ("kendoDraggable" in attrs) {
                                $timeout(function() {
                                    var properties = $parse(attrs["kendoDraggable"])(scope);
                                    iElem.kendoDraggable({
                                        filter: "li.k-item .k-in",
                                        hint: function(e) {
                                            var item = $("<div class='k-header k-drag-clue'><span class='k-icon k-drag-status k-denied'></span>" + e.html() + "</div>");
                                            return item;
                                        },
                                        drag: properties.drag,
                                        dragstart: properties.dragstart,
                                        dragend: properties.dragend,
                                        cursorOffset: {
                                            left: 10,
                                            top: 10
                                        }
                                    });
                                }, 0, false);
                            }

                            var edit = ("edit" in attrs) ? $parse(attrs["edit"])(scope) : true;

                            if (edit) {
                                var currentButtons = [];

                                gridoptions.select = function(e) {

                                    scope.selectedNode = undefined;
                                    $(currentButtons).each(function() {
                                        this.remove();
                                    });

                                    var tree = iElem.data("kendoTreeView");
                                    var dataItem = tree.dataItem(e.node);
                                    var $node = $(e.node);
                                    scope.selectedNode = $node;
                                    scope.selectedDataItem = dataItem;
                                    var $buttonTarget = $node.children("div");


                                    var $addButton = $(document.createElement("button"))
                                        .attr("ng-click", "add(selectedNode, selectedDataItem)")
                                        .append("<span class='k-icon k-add'></span>");

                                    currentButtons.push($addButton);
                                    $buttonTarget.append($addButton);
                                    $compile($addButton)(scope);

                                    var $editButton = $(document.createElement("button"))
                                        .attr("data-name", "group-tree-node-edit")
                                        .attr("ng-click", "edit(selectedNode, selectedDataItem)")
                                        .append("<span class='k-icon k-edit'></span>");

                                    currentButtons.push($editButton);
                                    $buttonTarget.append($editButton);
                                    $compile($editButton)(scope);

                                    var $deleteButton = $(document.createElement("button"))
                                        .attr("data-name", "group-tree-node-delete")
                                        .attr("ng-click", "delete(selectedNode, selectedDataItem)")
                                        .append("<span class='k-icon k-delete'></span>");

                                    currentButtons.push($deleteButton);
                                    $buttonTarget.append($deleteButton);
                                    $compile($deleteButton)(scope);
                                };
                            }
                            $compile($tree)(scope);

                            scope.add = function(node, dataItem) {
                                var modalWindow = $modal.open({
                                    templateUrl: "/static/app/components/componentEdit.html",
                                    backdrop: "static",
                                    controller: ["$scope",
                                        function($scope) {
                                            $scope.title = "Add component";
                                            $scope.component = {
                                                description: ""
                                            };
                                            $scope.cancel = function() {
                                                modalWindow.close();
                                            };
                                            $scope.submit = function() {
                                                //$http.post("/api/components", { childId: sourceDataItem.id })
                                                var component = {
                                                    description: $scope.component.description,
                                                    structure_parent_id: dataItem.id
                                                };
                                                componentService.save(component).$promise
                                                    .then(function(insertedComponent) {
                                                        var tree = node.closest("[kendo-tree-view]");
                                                        var treeview = tree.data("kendoTreeView");

                                                        dataItem.loaded(false);
                                                        treeview.append(insertedComponent, node);
                                                        dataItem.load();
                                                        modalWindow.close();
                                                    })
                                                    ["catch"](function(err) {
                                                        alert("An error occurred");
                                                    });
                                            };
                                        }
                                    ]
                                });
                            };

                            scope.edit = function(node, dataItem) {
                                componentService.get({id: dataItem.id}).$promise
                                    .then(function(retrievedComponent) {
                                        var modalWindow = $modal.open({
                                            templateUrl: "/static/app/components/componentEdit.html",
                                            backdrop: "static",
                                            controller: ["$scope",
                                                function($scope) {
                                                    $scope.title = "Edit Component";
                                                    $scope.component =  {
                                                        num: retrievedComponent.num,
                                                        description: retrievedComponent.description
                                                    };

                                                    $scope.cancel = function() {
                                                        modalWindow.close();
                                                    };

                                                    $scope.submit = function() {
                                                        componentService.update($scope.component).$promise
                                                            .then(function(data) {
                                                                var tree = node.closest("[kendo-tree-view]");
                                                                var treeview = tree.data("kendoTreeView");
                                                                node.find('span.k-in').first().text(data.name);
                                                                modalWindow.close();
                                                            }).catch(function(error) {
                                                                alert("An error occurred while trying to update the component.");
                                                            })
                                                    }
                                                }
                                            ]
                                        })
                                    });
                            };

                            scope.delete = function(node, dataItem) {
                                componentService.get({id: dataItem.id}).$promise
                                    .then(function(retrievedComponent) {
                                        var modalWindow = $modal.open({
                                            templateUrl: "/static/app/components/componentDelete.html",
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
                                                        componentService.delete({id: dataItem.id}).$promise
                                                            .then(function(data) {
                                                                var tree = node.closest("[kendo-tree-view]");
                                                                var treeview = tree.data("kendoTreeView");
                                                                treeview.remove(node);
                                                                modalWindow.close();
                                                            }).catch(function(error) {
                                                                alert("The component could not be deleted. " + error.data.message);
                                                            });
                                                    };
                                                }
                                            ]
                                        });
                                    });
                            };
                        }
                    };
                }
            };
        }
    ]);