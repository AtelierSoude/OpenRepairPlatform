
/// trick to make select2 works inna modal 
$(document).ready(function(){
$.fn.modal.Constructor.prototype._enforceFocus = function() {};
});

$(document).ready(function(){
/// festch api regardless to the selected user using autocomplete 
elem = document.querySelector("#id_user");
if (elem) {
    elem.onchange=function() {  
    if($(".selected-user").length){ 
        user_pk = $(".selected-user").attr('id');
        fetch("/api/user/"+user_pk)
        .then(response => {
            return response.json();
        })
        .then(data => {
            $("#id_email").val(data.email).val();
            $("#id_first_name").val(data.first_name).val();
            $("#id_last_name").val(data.last_name).val();
            $("#id_street_address").val(data.street_address).val();
        })
    }
    else { 
        $("#id_email").val('');
        $("#id_first_name").val('');
        $("#id_last_name").val('');
        $("#id_street_address").val('');
    };
    };
};
});
