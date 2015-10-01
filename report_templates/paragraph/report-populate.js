var getKeys = function(o) {
    var keys = [];
    for (var key in o)
        keys.push(key);

    return keys;
};

(function() {
    var $componentsDiv = $("#paragraphs");

    var $table = $(document.createElement("table"));
    $componentsDiv.append($table);

    var typeDescriptions = {
        "AR": "Acceptance Requirements",
        "CR": "Commissioning Requirements",
        "CS": "Control Sequences",
        "DR": "Demand Responses",
        "FT": "Functional Tests",
        "LC": "Load Curtailment",
        "MR": "Maintenance Requirements",
        "PR": "Project Requirements",
        "RR": "Roles and Responsibilities"
    }

    var printEquipmentTables = function() {
        for (var i = 0; i < window["report_options"].equipments.length; ++i) {
            printEquipmentTable(window["report_options"].equipments[i]);
        }
    };

    var printEquipmentTable = function(equipment) {
        var $table = $(document.createElement("table")).addClass("equipment_table");
        $componentsDiv.append($table);
        $table.append(
            $(document.createElement("thead")).append(
                $(document.createElement("tr")).addClass("equipment_name").append(
                    $(document.createElement("td")).text(equipment.equipment.name)
                )
            ).append(
                $(document.createElement("tr")).addClass("equipment_name_spacer").append(
                    $(document.createElement("td"))
                )
            )
        );

        printParagraphs(equipment.paragraphs, $table);

        //printParagraphsForType(equipment.components, "CS", $table);
    };

    var printParagraphs = function(paragraphsByType, $table) {
        var paragraphTypes = getKeys(paragraphsByType);
        paragraphTypes.sort();

        for (var i = 0; i < paragraphTypes.length; ++i) {
            var paragraphType = paragraphTypes[i];
            $table.append(
                $(document.createElement("tr")).addClass("paragraph_type_name").append(
                    $(document.createElement("td")).text(typeDescriptions[paragraphType])
                ))
            .append(
                $(document.createElement("tr")).addClass("paragraph_type_name_spacer").append(
                    $(document.createElement("td"))
                )
            );
            printParagraphsForType(paragraphsByType[paragraphType], $table);
        }
    };

    var printParagraphsForType = function(paragraphsByComponent, $table) {
        var componentNums = getKeys(paragraphsByComponent);
        componentNums.sort();

        for (var i = 0; i < componentNums.length; ++i) {
            var componentNum = componentNums[i];
            $table.append(
                $(document.createElement("tr")).append(
                    $(document.createElement("td")).addClass("component_name").text(componentNum)
                )
            );
            printParagraphsForComponent(paragraphsByComponent[componentNum], $table);
        }
    };

    var printParagraphsForComponent = function(paragraphsByCategory, $table) {
        var categoryNames = getKeys(paragraphsByCategory);
        categoryNames.sort();

        for (var i = 0; i < categoryNames.length; ++i) {
            var categoryName = categoryNames[i];
            $table.append(
                $(document.createElement("tr")).append(
                    $(document.createElement("td")).addClass("category_title").text(categoryName)
                )
            );
            printParagraphsForCategory(paragraphsByCategory[categoryName], $table);
        }
    };

    var printParagraphsForCategory = function(paragraphs, $table) {
        for (var i = 0; i < paragraphs.length; ++i) {
            var paragraph = paragraphs[i];

            $table.append(
                $(document.createElement("tr")).append(
                    $(document.createElement("td")).addClass("paragraph_title").text(paragraph.title)
                )
            ).append(
                $(document.createElement("tr")).append(
                    $(document.createElement("td")).addClass("paragraph_text").html(paragraph.description)
                )
            );
        }
    };

    printEquipmentTables();
})();