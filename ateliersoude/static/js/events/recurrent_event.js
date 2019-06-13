var recurrentType = document.querySelector('select[name=recurrent_type]')
var weeks = document.querySelectorAll('.for-month')
function checkRecurrentType () {
  if (recurrentType.value == 'MONTHLY') {
    weeks.forEach(function(elm){
      elm.disabled = false
    })
  } else {
    weeks.forEach(function(elm){
      elm.disabled = true
    })
  }
}
checkRecurrentType()
recurrentType.addEventListener("change",checkRecurrentType)
