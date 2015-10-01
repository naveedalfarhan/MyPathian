angular.module("pathianApp.controllers")
    .controller("groupsTreeCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "groupTreeFactory",
        function ($scope, $rootScope, $location, $http, $modal, groupTreeFactory) {
            $rootScope.global.linkpath = "#/admin/groups";

            $scope.treeOptions = {
                dataTextField: "name",
                dataSource: {
                    transport: {
                        read: {
                            url: "/api/groups/getChildrenOf",
                            dataType: "json"
                        }
                    },
                    schema: {
                        model: {
                            id: "id",
                            hasChildren: "childIds.length > 0"
                        }
                    }
                }
            };
            
            $scope.groupGridOptions = $rootScope.global.getJsonGridOptions({
                controllerName: "groups",
                model: {
                    id: "id",
                    fields: {
                        id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                        name: { type: "string", validation: { required: true } }
                    }
                },
                columns: ["name"],
                editable: false,
                createTemplate: false,
                defaultSort: { field: "name", dir: "asc" },
                other: {
                    filterable: {
                        extra: false,
                        operators: {
                            string: {
                                startswith: "Starts with",
                                eq: "Is equal to"
                            }
                        }
                    }
                }
            });

            $scope.groupGridOptions.options.dataSource = $scope.groupGridOptions.dataSource;
            $scope.groupGridOptions = $scope.groupGridOptions.options;


            var dropHint;
            $scope.gridDraggable = {
                dragstart: function(e) {
                    dropHint = $("<div class='k-drop-hint' />")
                        .css("visibility", "hidden");
                },
                dragend: function (e) {
                    groupTreeFactory.addChild(e.currentTarget[0], $(kendo.eventTarget(e)), this.hint, dropHint);
                    
                },
                dragcancel: function(e) {
                    dropHint.remove();
                },
                drag: function (e) {
                    var dropTarget = $(kendo.eventTarget(e));
                    var hoveredItem = dropTarget.closest(".k-top,.k-mid,.k-bot");
                    var hoveredTree = dropTarget.closest(".k-treeview");
                    var hoveredTreeObject = hoveredTree.data("kendoTreeView");

                    var statusClass = "k-denied";
                    if (hoveredItem.length) {
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
                    } else if (hoveredTreeObject !== null) {
                        statusClass = "k-add";
                    } else {
                        dropHint.css("visibility", "hidden");
                    }
                    
                    var statusElement = this.hint.find(".k-drag-status")[0];
                    statusElement.className = "k-icon k-drag-status " + statusClass;
                }
            };

            $scope.treeDropTarget = {
                dragenter: function() {
                    //console.log("dragenter");
                },
                dragleave: function () {
                    //console.log("dragleave");
                },
                drop: function () {
                    //console.log("drop");
                }
            };
        }
    ]);