function openPopup() {
    document.getElementById('popup').classList.remove('hide_popup');
    document.getElementById('popup-overlay').classList.remove('hide_popup');
}

function closePopup() {
    document.getElementById('popup').classList.add("hide_popup");
    document.getElementById('popup-overlay').classList.add("hide_popup");
}

function executeAction(Id) {
    const checkboxes = document.querySelectorAll('#checkboxForm input[type="checkbox"]:checked');
    let selectedOptions = [];
    checkboxes.forEach((checkbox) => {
        selectedOptions.push(checkbox.value);
    });
    fetch('/execute',{
        method: 'POST',
        body: JSON.stringify({selectedOptions: selectedOptions, Id: Id}),
    }).then((_res) => {
        window.location.href = "/folder/"+ Id;
    });
}

let selectAll = document.getElementById('selectAll');
selectAll.onclick = () => {
    let options = document.querySelectorAll('#checkboxForm input[type="checkbox"]:not(#selectAll)');
    if (selectAll.checked == true) {
        for (let i=0;i<options.length;i++) {
            options[i].checked = true;
        }
    } else {
        for (let i=0;i<options.length;i++) {
            options[i].checked = false;
        }
    }
}