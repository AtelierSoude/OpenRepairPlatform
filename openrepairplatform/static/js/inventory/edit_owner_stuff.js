
$(document).ready(function(){
    owner = document.querySelector("#ownerchoice");
      owner.onchange=function () {
        if($(this).val() == 'orga') {
            $("#id_member_owner").val("")
            $("#select2-id_member_owner-container").html('')
            $('#findorga').show()
            $('#finduser').hide()
        }
        else if($(this).val() == 'user') {
            $("#id_organization_owner").val("")
            $('#findorga').hide()
            $('#finduser').show()
        }
        else if($(this).val() == 'nobody') {
            $("#id_organization_owner").val("")
            $("#id_member_owner").val("")
            $("#select2-id_member_owner-container").html('')
            $('#findorga').hide()
            $('#finduser').hide()
        }
      }
  });