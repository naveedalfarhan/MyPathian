function wkhtmltopdfSubstitutions() {
    var vars={};

    //Get all variables/values in the url bar (aka after the ?)
    var variables_and_values_list = window.location.search.substring(1).split('&');
    for (var variable_and_value in variables_and_values_list) {
        //Split up the variable name/value
        var variable_and_value_list = variables_and_values_list[variable_and_value].split('=',2); //I have no idea why the 2 is there..expected 1

        //Store the variable as the index and the value as the value at that index
        vars[variable_and_value_list[0]] = unescape(variable_and_value_list[1]);
    }


    var substitution_trigger_words=['frompage','topage','page','webpage','section','subsection','subsubsection'];
    for (var word in substitution_trigger_words) {

        //Get all occurrences of this trigger word in the page when used as a class on a tag
        var elements_with_this_trigger_word = document.getElementsByClassName(substitution_trigger_words[word]);
        for (var elements_index=0; elements_index< elements_with_this_trigger_word.length; ++elements_index){

            //Replace the text of that tag with the value of that trigger word in the variable vars
            //since the indexes of vars are trigger words, that can be used to find the values for those trigger words
            elements_with_this_trigger_word[elements_index].textContent = vars[substitution_trigger_words[word]];
        }
    }
}