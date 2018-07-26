// Courtesy of https://www.w3schools.com/howto/howto_css_modals.asp

var modal = document.createElement("div");
modal.id = "modal";
modal.className += "js-modal";

var modal_content = document.createElement("div");
modal_content.className += "modal-content";
modal_content.id += "modal-content";

var modal_close = document.createElement("span");
modal_close.className += "close";
modal_close.id = "modal-close"
modal_close.innerHTML = "&times;"

var modal_message = document.createElement("p");

var modal_cancel_btn = document.createElement("button")
modal_cancel_btn.className += "btn btn-default"
modal_cancel_btn.innerHTML = "Annuler"
modal_cancel_btn.id = "modal-cancel"

var modal_accept_btn = document.createElement("button")
modal_accept_btn.className += "btn btn-primary"
modal_accept_btn.innerHTML = "Valider"
modal_accept_btn.id = "modal-accept"

modal_content.appendChild(modal_close);
modal_content.appendChild(modal_message);
modal_content.appendChild(modal_accept_btn);
modal_content.appendChild(modal_cancel_btn);
modal.appendChild(modal_content);
document.body.appendChild(modal);

function hide_modal(){
    let modal = document.getElementById('modal');
    modal.style.display = "none";
}

function create_modal_window(message, callback, args){
    modal_message.innerHTML = message;

    let accept_btn = document.getElementById("modal-accept");
    let cancel_btn = document.getElementById("modal-cancel");
    let span = document.getElementById("modal-close");
    modal.style.display = "block";

    // When the user clicks on the cancel button, close the modal
    cancel_btn.onclick = () => hide_modal();

    // When the user clicks on <span> (x), close the modal
    span.onclick = () => hide_modal();

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal)
            hide_modal()
    }

    accept_btn.onclick = function(){
        callback.apply(args);
        hide_modal();
    };
}
