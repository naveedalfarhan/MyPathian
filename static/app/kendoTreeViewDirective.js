angular.module("pathianApp.directives")
    .directive("selectableTreeView", ["$parse", "$timeout", "$compile",
        function($parse, $timeout, $compile) {

            return {
                priority: 900, // a high number to ensure this is the first directive that gets compiled
                terminal: true, // true indicates that this is the last directive that gets compiled
                // the two properties together ensure this is the only directive that gets compiled
                scope: true,
                compile: function (elem, attrs) {
                    // build the inner elements

                    var $tree = $(document.createElement("div"))
                        .attr("kendo-tree-view", "")
                        .attr("k-options", attrs["kOptions"])
                        .attr("kendo-drop-target", attrs["kendoDropTarget"]);

                    elem.append($tree);

                    return function(scope, iElem, attrs) {
                            var bindProp = attrs["ngBind"] ? $parse(attrs["ngBind"]) : null;
                            var modelProp = attrs["ngModel"] ? $parse(attrs["ngModel"]) : null;
                            var selectionStyle = attrs["selectionStyle"];


                            $compile(iElem.children("[kendo-tree-view]"))(scope);

                            $timeout(function(){
                                var tree = iElem.children("[kendo-tree-view]").data("kendoTreeView");

                                var addToScope = function(node) {
                                    if (!bindProp && !modelProp)
                                        return;
                                    if (bindProp)
                                        var checkedNodes = bindProp(scope);
                                    if (modelProp)
                                        var checkedNodes = modelProp(scope);
                                    checkedNodes.push({id:node.id, name:node.name});

                                    if (modelProp)
                                        modelProp.assign(scope.$parent, checkedNodes);

                                    scope.$apply();
                                };

                                var removeFromScope = function(node) {
                                    if (!bindProp && !modelProp)
                                        return;
                                    if (bindProp)
                                        var checkedNodes = bindProp(scope);
                                    if (modelProp)
                                        var checkedNodes = modelProp(scope);
                                    var checkedNodesIds = checkedNodes.map(function(node){return node.id});
                                    var index = checkedNodesIds.indexOf(node.id);
                                    checkedNodes.splice(index,1);

                                    if (modelProp)
                                        modelProp.assign(scope.$parent, checkedNodes);

                                    scope.$apply();
                                };

                                var updateTreeFromScope = function() {
                                    var scopePropSelected;
                                    if (selectionStyle == "multiple" || selectionStyle == "multi") {
                                        scopePropSelected = this(scope).map(function(node) { return node.id });
                                        if(scopePropSelected === undefined || scopePropSelected === null)
                                            return;

                                        var nodes = tree.dataSource.view();
                                        checkNodes(scopePropSelected, nodes);
                                    } else if (selectionStyle == "single") {
                                        scopePropSelected = this(scope) ? this(scope).id : null;
                                        if(scopePropSelected === undefined || scopePropSelected === null)
                                            return;

                                        var nodes = tree.dataSource.view();
                                        selectNode(scopePropSelected, nodes);
                                    }
                                };

                                function selectNode(selectedNodeId, nodes) {
                                    for(var i=0; i < nodes.length; i ++){
                                        if (selectedNodeId == nodes[i].id){
                                            var node = tree.findByUid(nodes[i].uid);
                                            tree.select(node);
                                        }

                                        if (nodes[i].hasChildren) {
                                            selectNode(selectedNodeId, nodes[i].children.view())
                                        }
                                    }
                                }

                                function checkNodes(selectedNodeIds, nodes) {
                                    for(var i=0; i < nodes.length; i ++){
                                        var checkitem = tree.findByUid(nodes[i].uid).find("> div > .k-checkbox > input[type='checkbox']");
                                        if (selectedNodeIds.indexOf(nodes[i].id) != -1){
                                            if (checkitem !== undefined && checkitem !== null){
                                                nodes[i].checked = true;
                                                $(checkitem).prop("checked", true);
                                            }
                                        }
                                        else {
                                            // uncheck node
                                            nodes[i].checked = false;
                                            $(checkitem).prop('checked', false);
                                        }

                                        if (nodes[i].hasChildren) {
                                            checkNodes(selectedNodeIds, nodes[i].children.view())
                                        }
                                    }
                                }

                                function uncheckNodes(nodeId, nodes) {
                                    for (var i=0; i < nodes.length; i ++){
                                        if (nodes[i].id == nodeId){
                                            nodes[i].checked = false;
                                            var uncheckitem = tree.findByUid(nodes[i].uid).find("> div > .k-checkbox > input[type='checkbox']");
                                            if (uncheckitem !== undefined && uncheckitem !== null)
                                                $(uncheckitem).prop("checked", false);
                                        }

                                        if (nodes[i].hasChildren){
                                            uncheckNodes(nodeId, nodes[i].children.view())
                                        }
                                    }
                                }


                                if (selectionStyle == "multi" || selectionStyle == "multiple") {
                                    tree.dataSource.bind("change", function(e) {
                                        if (e.field === "checked"){
                                            if (e.items[0].checked === false){
                                                uncheckNodes(e.items[0].id, tree.dataSource.view());
                                                removeFromScope(e.items[0]);
                                            }else{
                                                addToScope(e.items[0]);
                                            }
                                        }
                                    });


                                    // updateTreeFromScope.bind(bindProp) returns a function that when called, will call
                                    // updateTreeFromScope with bindProp set as this.

                                    // updateTreeFromScope.call(bindProp) === updateTreeFromScope.bind(bindProp)()

                                    if (bindProp) {
                                        var call = updateTreeFromScope.bind(bindProp);
                                        scope.$watchCollection(attrs["ngBind"], call);
                                        tree.bind("dataBound", call);
                                    }
                                    if (modelProp) {
                                        var call = updateTreeFromScope.bind(modelProp);
                                        scope.$watchCollection(attrs["ngModel"], call);
                                        tree.bind("dataBound", call);
                                    }
                                } else if (selectionStyle == "single") {
                                    tree.bind("select", function(e) {
                                        if (!modelProp)
                                            return;

                                        var dataItem = tree.dataItem(e.node);
                                        var o = { id: dataItem.id, name: dataItem.name };
                                        modelProp.assign(scope.$parent, o);
                                        scope.$apply();
                                        console.log(o);
                                    });

                                    if (bindProp) {
                                        var call = updateTreeFromScope.bind(bindProp);
                                        scope.$watch(attrs["ngBind"], call);
                                        tree.bind("dataBound", call);
                                    }
                                    if (modelProp) {
                                        var call = updateTreeFromScope.bind(modelProp);
                                        scope.$watch(attrs["ngModel"], call);
                                        tree.bind("dataBound", call);
                                    }
                                }



                            }, 100, false);
                        };

                }
            }
        }
    ])