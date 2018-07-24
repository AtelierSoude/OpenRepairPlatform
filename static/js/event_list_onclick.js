function create_message(event, keyword){
    message = "Êtes vous sûr de vouloir "
    message += keyword + " "
    message += event.title
    message += " du "
    message += event.day_month_str
    message += " de "
    message += event.starts_at
    message += " à "
    message += event.ends_at
    message += "?"

    return message;
}

function event_list_onclick(x){
    var purpose = x.attributes.purpose.value
    var event = app.event_list.filter(event => (event.pk == x.id))[0];
    var message = "";
    var callback;
    var csrftoken = getCookie('csrftoken');
    var headers = new Headers();
    headers.append('Content-Type', 'application/x-ww-form-urlencoded; charset=UTF-8');
    headers.append('X-CSRFToken', csrftoken);
    var payload = {
        event_id: parseInt(x.id),
    }
    var formData = payload_to_formBody(payload);

    switch (purpose){
    case 'trash':
        message = create_message(event, "supprimer l'événement");
        callback = function(event){
            fetch('/api/deleteEvent/', {
                headers: headers,
                method: "POST",
                body: formData,
                credentials: 'include',
            })
                .then(handleErrors)
                .then(function(res){ return res.json(); })
                .then(function(data){
                    //if deleted successfully
                    if (data['status'] != -1)
                        //delete event from list
                        app.event_list = app.event_list.filter(event => (event.pk != x.id));
                });
        }
        break;
    case 'book':
        message = create_message(event, "réserver pour");
        callback = function(event){
            fetch('/api/book/', {
                headers: headers,
                method: "POST",
                body: formData,
                credentials: 'include',
            })
                .then(handleErrors)
                .then(function(res){ return res.json(); })
                .then(function(data){
                });
        }
        break;
    case 'cancel':
        message = create_message(event, "annuler votre réservation pour");
        callback = function(event){
        }
        break;
    default:
        message = "Switch error";
        callback = function(){
            console.log("there has been an issue with parameter parsing");
        }
    }

    create_modal_window(message, callback, [event]);
}
