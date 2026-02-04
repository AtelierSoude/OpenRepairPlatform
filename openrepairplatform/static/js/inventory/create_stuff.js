$(document).ready(function () {

  // ICI on regarde quel bouton submit a été cliqué afin de pouvoir renvoyer create_print via data-submit-action
  // C'est pas très beau , à revoir un jour 
  

  var myModalEl = document.getElementById('modal')

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-submit-action]');
    if (!btn) return;

    const form = btn.closest('form');
    if (!form) return;

    const hidden = form.querySelector('#id_submit_action, input[name="submit_action"]');
    if (!hidden) return;

    hidden.value = btn.getAttribute('data-submit-action') || '';
  }, true);
  
  myModalEl.addEventListener('show.bs.modal', function (event) {

    function clearSelect2(id) {
      const $el = $(id);
      if ($el.length) {
        $el.val(null).trigger('change'); // clear select2 autocomplete suggestions
      }
    }
    // affichage des champs au fil de l'eau 


    category = document.querySelector("#id_category");

    if (category) {
      category.onchange = function () {
          clearSelect2('#id_device');
          clearSelect2('#id_observation');
          clearSelect2('#id_reasoning');
          clearSelect2('#id_action');
          clearSelect2('#id_status');
        if ($(this).val()) {
          $("#devicesearch").show()
        }
      };
    }
    device = document.querySelector("#id_device");
    if (device) {
      device.onchange = function () {
        if ($(this).val()) {
          $("#stuffcreate").show()
          $("#btnsubmit").show()
          $("#btnsubmitandprint").show()
        }
      };
    }
    $("#id_create_folder").click(function () {
      if ($("#id_create_folder").is(":checked")) {
        $("#addfolder").show()
      }
      else {
        $("#addfolder").hide()
      }
    });
    $("#id_create_device").click(function () {
      if ($("#id_create_device").is(":checked")) {
        $("#adddevice").show()
        $("#stuffcreate").show()
        $("#btnsubmit").show()
        $("#btnsubmitandprint").show()
        $(".device-search-form").hide()
        $("#id_device").val("")
        $("#select2-id_device-container").html('')
      }
      else {
        $("#adddevice").hide()
        $("#stuffcreate").hide()
        $("#btnsubmit").hide()
        $("#btnsubmitandprint").hide()
        $(".device-search-form").show()
      }
    });

  })
});
