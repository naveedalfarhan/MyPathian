angular.module("pathianApp.controllers")
    .controller("uploadGroupDataCtrl", [
        "$scope", "$rootScope", "$location",
        function ($scope, $rootScope, $location) {
            $rootScope.global.linkpath = "#/reporting/uploadGroupData";

            $scope.model = {
                group: null,
                account: null
            };

            $scope.page = "selectGroup";

            $scope.changePage = function(newPage) {
                if (newPage == "selectAccount") {
                    $scope.page = "selectAccount";
                    $scope.model.account = null;
                    setAccountGridOptions($scope.model.group.id);
                } else if (newPage == "selectGroup") {
                    $scope.page = "selectGroup";
                } else if (newPage == "selectFile") {
                    $scope.page = "selectFile";
                    setFileUploadOptions($scope.model.account.id);
                }
            };

            $scope.groupTreeOptions = {
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

            var setAccountGridOptions = function(groupId) {

                $scope.accountGridOptions = $rootScope.global.getJsonGridOptions({
                    controllerName: "groups/" + groupId + "/accounts",
                    model: {
                        id: "id",
                        fields: {
                            id: { type: "string", editable: false, nullable: true, defaultValue: undefined },
                            name: { type: "string", validation: { required: true } },
                            num: { type: "string", validation: { required: true } }
                        }
                    },
                    columns: ["name", "num"],
                    createTemplate: false,
                    editable: false,
                    defaultSort: { field: "Name", dir: "asc" }
                });
            };

            var setFileUploadOptions = function(accountId) {
                $scope.fileUploadOptions = {
                    url: "/api/uploadForAccount/" + accountId,
                    done: function() {
                        $location.path("/reporting/uploadProgress");
                    }
                };


                $scope.uploadAsyncProps = {
                    saveUrl: '/api/uploadForAccount/' + accountId,
                    autoUpload: false
                };
            };

            $scope.uploadSuccess = function() {
                $location.path("/reporting/uploadProgress");
                $scope.$apply();
            };
        }
    ]);