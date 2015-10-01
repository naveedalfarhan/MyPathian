angular.module("pathianApp.directives")
    .directive("equipmentManagerTree", ["$parse", "$timeout", "$compile",
        function ($parse, $timeout, $compile) {
            return {
                priority: 1000, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: {
                    ngModel: "="
                },
                compile: function (elem, attrs) {
                    // build the inner elements
                    var $tree = $(document.createElement("div"))
                        .attr("kendo-tree-view", "")
                        .attr("k-options", "treeOptions");

                    elem.replaceWith($tree);

                    return {
                        post: function (scope, iElem, iAttrs) {
                            // just because we added the angular directives to the kendo grid div above doesn't
                            // mean they get automatically compiled... we have to find the grid and tell it to compile

                            scope.selected = {};
                            scope.testProp = false;
                            scope.treeOptions = {
                                template: "#=item.name#",
                                dataSource: {
                                    transport: {
                                        read: {
                                            url: "/api/equipment/managerTree",
                                            dataType: "json"
                                        }
                                    },
                                    schema: {
                                        model: {
                                            id: "id",
                                            hasChildren: "hasChildren"
                                        }
                                    }
                                },
                                checkboxes: {
                                    template: "# if (item.id.substring(0,10) === 'equipment:') {# <input type='checkbox' />#}#"
                                }
                            };

                            if (!scope.ngModel)
                                scope.ngModel = [];

                            iElem.on("change", "input:checkbox", function() {
                                var self = this;
                                var $this = $(self);
                                scope.$apply(function() {
                                    var uid = $this.closest("li[role='treeitem']").data().uid;
                                    var treeview = $this.closest("[data-role='treeview']").data().kendoTreeView;
                                    var dataItem = treeview.dataSource.getByUid(uid);

                                    for (var i = 0; i < scope.ngModel.length; ++i) {
                                        if (scope.ngModel[i].id == dataItem.equipment_id) {
                                            if (self.checked)
                                                return;
                                            else {
                                                scope.ngModel.splice(i, 1);
                                                return;
                                            }
                                        }
                                    }

                                    // if execution reaches down here, item was not in ngModel list... at this point,
                                    // if the checkbox was checked, we add it

                                    if (self.checked) {
                                        scope.ngModel.push({
                                            "id": dataItem.equipment_id, "name": dataItem.name,
                                            "group_id": dataItem.group_id, "group_name": dataItem.group_name
                                        });
                                    }
                                });
                            });


                            $compile(iElem)(scope);
                        }
                    };
                }
            };
        }
    ]);