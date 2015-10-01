angular.module("pathianApp.controllers")
    .controller("componentsStructureTreeCtrl", ["$scope", "$rootScope", "$location", "$http", "$modal", "componentService",
        function ($scope, $rootScope, $location, $http, $modal, componentService) {
            $rootScope.global.linkpath = "#/admin/components";

            $scope.userPermissions = $rootScope.global.userPermissions;

            $scope.treeOptions = {
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
        }
    ]);