function autocompleteUserInfo() {
    elem = document.querySelector("#id_user")
    if (elem) {
        elem.onchange=function() {
          user = document.querySelector(".selected-user")
          if(user) {
            user_pk = user.getAttribute('id')
            fetch(`/api/user/${user_pk}`).then(response => { return response.json() }).then(data => {
              document.querySelector("#id_email").value = data.email
              document.querySelector("#id_first_name").value = data.first_name
              document.querySelector("#id_last_name").value = data.last_name
              document.querySelector("#id_street_address").value = data.street_address
            })
          }
          else {
              document.querySelector("#id_email").value = ''
              document.querySelector("#id_first_name").value = ''
              document.querySelector("#id_last_name").value = ''
              document.querySelector("#id_street_address").value = ''
          }
        }
    }
}

