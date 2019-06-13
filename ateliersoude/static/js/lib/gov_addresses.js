// Used to stop old ongoing request
let fetchController = new AbortController();
let signal = fetchController.signal;

if (typeof addressFound === 'undefined') {
    addressFound = () => {};
}
if (typeof addrSelected === 'undefined') {
    addrSelected = () => {};
}

function queryGovAddrAPI(lookupAddresses, suggest) {
    fetch(lookupAddresses, {
        method: 'get',
        signal: signal,
    }).then(function (res) {
        return res.json();
    }).then(function (data) {
        if (!data.features) {
            suggest([]);
            return;
        }
        let addrSuggestions = data.features.map(
            f => {
                addressFound(f);
                return f.properties.label;
            }
        );
        suggest(addrSuggestions);
    }).catch(function (err) {
        if (err.name !== "AbortError") {
            console.error(` Err: ${err}`);
        }
    });
}

let elements = document.querySelectorAll(inputSelector);
elements.forEach(function (node) {
    new autoComplete({
        selector: node,
        onSelect: addrSelected,
        delay: 30,
        source: function(addr, suggest){
            let search = encodeURIComponent(addr);
            let lookupAddresses = "https://api-adresse.data.gouv.fr/search/?limit=15&lat=45.76&lon=4.84&q=" + search;

            // abort running fetch requests
            fetchController.abort();
            fetchController = new AbortController();
            signal = fetchController.signal;

            queryGovAddrAPI(lookupAddresses, suggest);
        }
    });
});
