let inputEmailSelector = 'input[name="email"]';
let inputMainFieldSelector = 'input[name="main_field"]';
var inputs = [
    ...document.querySelectorAll(inputEmailSelector),
    ...document.querySelectorAll(inputMainFieldSelector)
]
var choices;

function titleCase(str) {
    return str.toLowerCase().split(' ').map(function(word) {
        return word.replace(word[0], word[0].toUpperCase());
    }).join(' ');
}

inputs.forEach(function (node) {
    new autoComplete({
        selector: node,
        minChars: 3,
        source: function(user, suggest){
            let term = user.toLowerCase();
            let choices_id = (node.name == "main_field") ? 'members-data' : 'emails-data';
            let choices = JSON.parse(document.getElementById(choices_id).textContent);
            let matches = [];
            for (let i=0; i<choices.length; i++) {
                let searchableString = (node.name == "main_field") ? choices[i].toLowerCase() : choices[i][0].toLowerCase();
                if (searchableString.includes(term)) {
                    matches.push(choices[i]);
                }
            }
            suggest(matches);
        },
        renderItem: function (item, search){
            if (node.name == "main_field") {
                return '<div class="autocomplete-suggestion" data-val="' + item + '">' + item +'</div>';
            } else {
                search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                let re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
                return '<div class="autocomplete-suggestion" data-val="' + item[1] + '">' + item[0].replace(re, "<b>$1</b>") + '</div>';
            }
        },
    });
});
