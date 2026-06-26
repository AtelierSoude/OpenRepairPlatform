  window.setTimeout(function() {
    $(".alert:not(.alert-stay)").css("right",'-1000px').slideUp(1000, function(){
        $(this).remove(); 
    });
  }, 4000);
  $(document).ready(function(){
      $(".alert:not(.alert-stay)").css("right",'0px');
  });