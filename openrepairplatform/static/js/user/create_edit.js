let inputSelector = 'input[name="street_address"]';

document.addEventListener('DOMContentLoaded', (e) => {
    var addButtons = document.getElementsByClassName("bs-gobal-modal");
    for (var index=0; index < addButtons.length; index++) {
  console.log();
      modalForm(addButtons[index], {
        formURL: addButtons[index]["dataset"]["formUrl"],
        isDeleteForm: false
      });
    }
  });
