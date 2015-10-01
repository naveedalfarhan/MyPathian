angular.module("pathianApp.directives")
    .directive("notificationList", ["$parse", "$compile", "$location", "userService",
        function($parse, $compile, $location, userService) {
            return {
                link: function(scope, elem, attrs) {
                    var id = $parse(attrs['notificationList'])(scope);
                    var fullList = attrs['fullList'];

                    userService.notifications({'id':id}, function(data) {
                        var $list = $(document.createElement("ul"))
                            .attr('style', 'list-style:none');

                        // Only display the entire list if on the notifications page or if there is only one notification
                        if ((fullList !== undefined && fullList !== null) || data.length === 1){
                            addEntireList($list, data);
                        } else if (data.length > 1) {
                            // More than one notification, so show a link to view all notifications
                            $list.append("<li><div class='alert alert-warning'>You have multiple notifications. To view them, please <a href='#/home/notifications'>click here</a>.</div></li>");
                        }


                        elem.replaceWith($list);
                        $compile($list)(scope);
                    });

                    function addEntireList($list, data) {
                        data.forEach(function (entry) {
                            $list.append("<li><div class='alert alert-warning alert-dismissable'><button type='button' class='close' data-dismiss='alert' aria-hidden='true' ng-click='removeNotification(\"" + entry.id + "\")'>&times;</button>" + entry.text + "</div></li>");
                        });
                    }
                }
            }
        }
    ]);