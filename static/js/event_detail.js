function refresh_buttons(){
    buttons = document.querySelectorAll("button.btn-setPresent")
    buttons.forEach(button => setEventHandler(button));
}

function setEventHandler(button){
    button.onclick = () => setPresent(button.id);
}

function updateCSS(data){
    console.log(data)
    square = document.getElementById("square-"+data['user_id']);
    square.className = "row border border-success checked"
}

function setPresent(id){
    let payload = {
        idents: id
    }
    var user_id;
    var view_model = this;
    var formBody = payload_to_formBody(payload);
    fetch('/api/setPresent/', {
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        method: "POST",
        body: formBody
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){ updateCSS(data)});
}

function payload_to_formBody(payload){
    var formBody = [];
    for (var property in payload) {
        var encodedKey = encodeURIComponent(property);
        var encodedValue = encodeURIComponent(payload[property]);
        formBody.push(encodedKey + "=" + encodedValue);
    }
    formBody = formBody.join("&");
    return formBody;
}

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}



refresh_buttons();
