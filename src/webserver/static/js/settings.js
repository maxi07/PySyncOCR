document.addEventListener('DOMContentLoaded', function () {
    const openai_button = document.getElementById("save-button");
    if (document.getElementById('openai_key').value.length > 0) {
        openai_button.textContent = "Disable"
        openai_button.disabled = false;
    } else {
        openai_button.textContent = "Enable"
    }
});


function submitOpenAI(event) {
    event.preventDefault(); // Prevent default form submission
    const submitButton = document.getElementById('save-button');
    const keyInput = document.getElementById('openai_key');
    submitButton.innerText = "Testing key...";
    submitButton.disabled = true;

    var formData = new FormData(document.getElementById('openai-form'));
    var xhr = new XMLHttpRequest();

    xhr.open('POST', '/settings/openai', true);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(response);
                if (response.success) {
                    animateButton(document.getElementById('save-button'), true);
                } else {
                    animateButton(document.getElementById('save-button'), false);
                }
            } else {
                console.error('Error:', xhr.status);
                console.error('Error:', xhr.responseText);
                animateButton(document.getElementById('save-button'), false);
            }
        }
    };

    xhr.send(formData);
}

function animateButton(button, success) {
    button.classList.add('disabled');
  
    if (success) {
        button.classList.add('success-color');
        button.innerHTML = '<i class="bi bi-check"></i> Success';
    } else {
        button.classList.add('failure-color');
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Failed';
    }
    
    setTimeout(function() {
        button.classList.remove('success-color', 'failure-color', 'disabled');
        button.innerHTML = 'Enable';
    }, 3000);
}

function checkIfEmpty(input_id, button_id) {
    var element = document.getElementById(input_id);
    var button = document.getElementById(button_id);
    if (element.value.length == 0) {
        element.classList.add('is-invalid');
        button.disabled = true;
    } else {
        element.classList.remove('is-invalid');
        button.disabled = false;
    }
}
