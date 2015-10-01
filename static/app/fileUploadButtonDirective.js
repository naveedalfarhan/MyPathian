angular.module("pathianApp.directives")
    .directive("fileUploadButton", ["$parse", "$timeout", "$compile",
        function($parse, $timeout, $compile) {
            return {
                template: "<button class='fileinput-button'><span>Browse</span><input type='file' name='{{fileUploaderName}}'></button>",
                replace: true,
                link: function(scope, elem, attrs) {
                    scope["fileUploaderName"] = "ngName" in attrs ? $parse(attrs["ngName"])(scope) : "files[]";
                    var ngModelGetter = "ngModel" in attrs ? $parse(attrs["ngModel"]) : null;
                    var fileElementGetter = "fileElement" in attrs ? $parse(attrs["fileElement"]) : null;

                    elem.find("input[type='file']").on("change", function() {
                        if (ngModelGetter)
                            ngModelGetter.assign(scope, this.files);
                        if (fileElementGetter)
                            fileElementGetter.assign(scope, this);
                        scope.$apply();
                    });
                }
            };
        }
    ]);