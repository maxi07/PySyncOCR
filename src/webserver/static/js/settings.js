document.addEventListener('DOMContentLoaded', function () {
    var onedriveNameInput = document.getElementById('onedrive_name');
    var submitButton = document.getElementById('add_onedrive_button');
    const errormsg = document.getElementById("allowedCharsErrorMsg");

    // Add an input event listener to the text input
    onedriveNameInput.addEventListener('input', function () {
        // Enable or disable the button based on whether the input has content
        submitButton.disabled = !onedriveNameInput.value.trim();

        // Validate the input
        if (validateTextInput(onedriveNameInput.value)) {
            onedriveNameInput.classList.remove('is-invalid');
            errormsg.style.display = 'none';
        } else {
            onedriveNameInput.classList.add('is-invalid');
            errormsg.style.display = 'block';
        }
    });
});

function deleteOneDriveConf(id) {
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/settings/onedrive', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                console.log(xhr.responseText);
                // Fade out the row before removing it
                const row = document.getElementById(id + '_row'); 
                // Fade animation
                row.style.transition = 'opacity 1.5s';
                row.style.opacity = 0;

                // Remove after fade
                setTimeout(() => {
                row.remove(); 
                }, 500);
            };
        };
    }
    xhr.send(JSON.stringify({"id": id}));
}

function addOneDrive() {
    const animation = document.getElementById("waitingAnimation");
    const form = document.getElementById("onedrive_name_container");
    const addButton = document.getElementById("add_onedrive_button");
    const statusUpdateElement = document.getElementById("statusUpdate");
    addButton.style.disabled = true;
    animation.style.display = "block";
    form.style.display = "none";

    const socket = new WebSocket('ws://' + window.location.host + '/websocket-onedrive');
    socket.addEventListener('message', ev => {
        statusUpdateElement.style.display = "block";
        console.log(ev.data);
        // Test if ev.data begins with 'http'
        if (ev.data.startsWith("http")) {
            // If it does, it's a link to the file
            document.getElementById("updateText").innerHTML = '<a href="' + ev.data + '" target="_blank">' + "To authenticate, please visit <br>" + ev.data + '</a>';
            window.open(ev.data, '_blank');
        } else if (ev.data.startsWith("Success")) {
            window.location.reload();
        } else {
            // Otherwise, it's just text
            animation.style.display = "none";
            document.getElementById("updateText").innerHTML = ev.data;
        }
    });
    socket.addEventListener('open', ev => {
        console.log('Connected to websocket');
        socket.send(JSON.stringify({ "name": document.getElementById("onedrive_name").value }));
    });
}


function validateTextInput(input) {
    // Regular expression pattern for allowed characters
    const pattern = /^[0-9A-Za-z_\- ]+$/;

    // Check if the input matches the pattern and does not start or end with a space
    if (pattern.test(input) && !input.startsWith(' ') && !input.endsWith(' ')) {
        return true; // Input is valid
    } else {
        return false; // Input is not valid
    }
}