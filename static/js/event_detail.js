function refresh_buttons(){
    btn_present = document.querySelectorAll("button.btn-setPresent")
    btn_present.forEach(button => setEventHandler(button, setPresent));
    btn_cancel = document.querySelectorAll("button.btn-setAbsent")
    btn_cancel.forEach(button => setEventHandler(button, setAbsent));
}

function setEventHandler(button, fn){
    button.onclick = () => fn(button.id);
}

function updateCSS_to_present(data, button_id){
    square = document.getElementById("square-"+data['user_id']);
    square.className = "row checked"
    button = document.getElementById(button_id);
    button.className = "btn-setAbsent btn";
    button.textContent = "Annuler présence";
    refresh_buttons();
}

function updateCSS_to_absent(data, button_id){
    square = document.getElementById("square-"+data['user_id']);
    square.className = "row"
    button = document.getElementById(button_id);
    button.className = "btn-setPresent btn";
    button.textContent = "Confirmer présence";
    refresh_buttons();
}

function setPresent(id){
    let payload = {
        idents: id
    }
    var formBody = payload_to_formBody(payload);
    fetch('/api/setPresent/', {
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        method: "POST",
        body: formBody
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){ updateCSS_to_present(data, id)});
}

function setAbsent(id){
    let payload = {
        idents: id
    }
    var formBody = payload_to_formBody(payload);
    fetch('/api/setAbsent/', {
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        method: "POST",
        body: formBody
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){ updateCSS_to_absent(data, id)});
}

refresh_buttons();
