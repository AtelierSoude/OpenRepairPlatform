$(document).ready(function() {
    $(".event").mouseover(
          function() {
            var location_id = $(this).data("location")
            $(this).addClass("shadow")
            $(this).removeClass("shadow-sm")
            $(".awesome-marker[data-location='" + location_id +"' ]").addClass("awesome-marker_hover")
          }
        );
    $(".event").mouseleave(
      function() {
        var location_id = $(this).data("location")
        $(this).removeClass("shadow")
        $(this).addClass("shadow-sm")
        $(".awesome-marker[data-location='" + location_id +"' ]").removeClass("awesome-marker_hover")
      }
    );
  });

var waypoint = new Waypoint({
  element: $('.event')[0],
  handler: function(shadows) {
    $(".event").mouseover(
          function() {
            var location_id = $(this).data("location")
            $(this).addClass("box-shadow")
            $(".awesome-marker[data-location='" + location_id +"' ]").addClass("awesome-marker_hover")
            $(".awesome-marker[data-location='" + location_id +"' ]").click()
          }
        );
    $(".event").mouseleave(
      function() {
        var location_id = $(this).data("location")
        $(this).removeClass("box-shadow")
        $(".awesome-marker[data-location='" + location_id +"' ]").removeClass("awesome-marker_hover")
      }
    );
  }
})
var infinite = new Waypoint.Infinite({
    element: $('.infinite-container')[0],
    onBeforePageLoad: function () {
      $('.loading').show();
    },
    onAfterPageLoad: function ($items) {
      $('.loading').hide();
    }
  });