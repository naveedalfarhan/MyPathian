angular.module("pathianApp.directives")
    .directive("kendoDraggable", ["$parse", "$timeout", "$compile",
        function($parse, $timeout) {
            return {
                link: function(scope, elem, attrs) {
                    var properties = $parse(attrs["kendoDraggable"])(scope);
                    console.log(properties);
                    $timeout(function() {
                        elem.kendoDraggable({
                            filter: "tr",
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
            };
        }
    ])
    .directive("kendoDropTarget", ["$parse", "$timeout", "$compile",
        function($parse, $timeout) {
            return {
                link: function (scope, elem, attrs) {
                    var properties = $parse(attrs["kendoDropTarget"])(scope);
                    
                    $timeout(function () {
                        console.log(elem.data("kendoTreeView"));

                        var bindLis = function() {
                            elem.find("li").kendoDropTarget({
                                dragenter: properties.dragenter,
                                dragleave: properties.dragleave,
                                drop: properties.drop
                            });
                        };

                        elem.data("kendoTreeView").bind("dataBound", bindLis);
                        bindLis();
                    }, 100, false);
                }
            };
        }
    ]);