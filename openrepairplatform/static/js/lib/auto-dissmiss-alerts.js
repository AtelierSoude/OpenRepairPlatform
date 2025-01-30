  window.setTimeout(function() {
    $(".alert").css("right",'-1000px').slideUp(1000, function(){
        $(this).remove(); 
    });
  }, 4000);
  $(document).ready(function(){
      $(".alert").css("right",'0px');
  });  
