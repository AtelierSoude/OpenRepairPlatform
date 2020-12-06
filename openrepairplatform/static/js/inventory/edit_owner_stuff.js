$(document).ready(function(){
    $.fn.modal.Constructor.prototype._enforceFocus = function() {};
      $("#ownerchoice").change(function () {
      var selected_option = $('#ownerchoice').val();
  
      if(selected_option === 'orga') {
          $('#findorga').show();
          $('#finduser').hide();
      }
      if(selected_option == 'user') {
          $('#findorga').hide();
          $('#finduser').show();
      }
      if(selected_option == 'nobody') {
          $('#findorga').hide();
          $('#finduser').hide();
          $("#id_organization_owner").val("");
          $("#id_member_owner").val("");
      }
      })
  });