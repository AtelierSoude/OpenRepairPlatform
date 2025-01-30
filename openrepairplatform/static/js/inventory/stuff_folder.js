
$(document).ready(function () {
    var myModalEl = document.getElementById('modal')
    myModalEl.addEventListener('show.bs.modal', function (event) {
        $("#id_change_stuff_state").change(function () {
            if($(this).is(":checked")) {
                $('#changestate').show();
            }
            else {
                $('#changestate').hide();
            }
        })
    }); 
});