$(document).ready(function () {
  var myModalEl = document.getElementById('modal')
  myModalEl.addEventListener('show.bs.modal', function (event) {

    category = document.querySelector("#id_category");

    if (category) {
      category.onchange = function () {
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
        $(".device-search-form").hide()
        $("#id_device").val("")
        $("#select2-id_device-container").html('')
      }
      else {
        $("#adddevice").hide()
        $("#stuffcreate").hide()
        $("#btnsubmit").hide()
        $(".device-search-form").show()
      }
    });

  })
});
