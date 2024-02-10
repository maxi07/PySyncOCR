const onedriveLocalListGroup = document.getElementById('onedrivelistgroup');
var onedriveDirLevel = 1;
var currentOneDrivePath = "/"; // The path we are currently in
var currentOneDriveSelectedPath = ""; // The path the user actually selected

document.addEventListener('DOMContentLoaded', function () {
    var onedriveNameInput = document.getElementById('onedrive_name');
    var submitButtonOneDriveConnections = document.getElementById('add_onedrive_button');
    var submitButtonpathmapping = document.getElementById('add_path_mapping_button');
    const errormsgOneDriveConn = document.getElementById("allowedCharsErrorMsgOneDriveConn");
    const errormsglocalpath = document.getElementById("allowedCharsErrorMsgLocalPath");
    var localpathinput = document.getElementById('local_path');

    // Add an input event listener to the text input
    onedriveNameInput.addEventListener('input', function () {
        // Enable or disable the button based on whether the input has content
        submitButtonOneDriveConnections.disabled = !onedriveNameInput.value.trim();

        // Validate the input
        if (validateTextInput(onedriveNameInput.value)) {
            onedriveNameInput.classList.remove('is-invalid');
            errormsgOneDriveConn.style.display = 'none';
            submitButtonOneDriveConnections.disabled = false;
        } else {
            onedriveNameInput.classList.add('is-invalid');
            errormsgOneDriveConn.style.display = 'block';
            submitButtonOneDriveConnections.disabled = true;
        }
    });

    // Add an input event listener to the local path input
    localpathinput.addEventListener('input', function () {
        // Validate the input
        if (validateTextInput(localpathinput.value)) {
            localpathinput.classList.remove('is-invalid');
            errormsglocalpath.style.display = 'none';
        } else {
            localpathinput.classList.add('is-invalid');
            errormsglocalpath.style.display = 'block';
        }
        evaluatePathMappingSubmitButton();
    });

    // Add event listener for when path mapping modal is hidden
    const pathmappingmodal = document.getElementById('pathmappingmodal')
    pathmappingmodal.addEventListener('hidden.bs.modal', event => {
        resetPathMappingModal();
    })

    const remotepathselector = document.getElementById("remotepathselector");
    // Event listener for when the collapse is about to be shown
    remotepathselector.addEventListener('show.bs.collapse', function () {
        console.log('Collapse is about to be shown.');
        loadOneDriveDir();
    });
});

function evaluatePathMappingSubmitButton() {
    const submitButtonpathmapping = document.getElementById('add_path_mapping_button');
    const localpathinput = document.getElementById('local_path');
    const remotePathInput = document.getElementById('remote_path');

    // Enable or disable the button based on whether the input has content
    submitButtonpathmapping.disabled = !localpathinput.value.trim();
    submitButtonpathmapping.disabled = localpathinput.classList.contains('is-invalid');
    submitButtonpathmapping.disabled = !remotePathInput.value.startsWith('/');
}

function deleteOneDriveConf(id) {
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/sync/onedrive', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
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
    xhr.send(JSON.stringify({ "id": id }));
}

function addOneDrive() {
    const animation = document.getElementById("waitingAnimationonedriveadd");
    const animation_statustext = document.getElementById("waitingAnimationonedriveadd_statustext");
    const form = document.getElementById("onedrive_name_container");
    const addButton = document.getElementById("add_onedrive_button");
    const statusUpdateElement = document.getElementById("statusUpdate");
    const sshTunnelInfoElement = document.getElementById("sshTunnelSetupInfo");
    const sshInstallInfoElement = document.getElementById("sshInstallInfo");
    const cloud_header = document.getElementById("cloud_header");
    const sshErrorMsg = document.getElementById("sshErrorMsg");
    addButton.style.disabled = true;
    animation.style.display = "block";
    form.style.display = "none";
    cloud_header.style.display = "none";

    // Check if ssh is enabled. We need a ssh tunnel for proper authentication with onedrive (duh..)
    animation_statustext.innerText = "Checking if SSH is enabled...";
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/sync/check-ssh', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            animation.style.display = "none";
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                sshErrorMsg.innerText = xhr.responseText;
                addButton.innerText = "Retry";
                // Show the ssh setup modal
                sshInstallInfoElement.style.display = "block";
            } else {
                console.log(xhr.responseText);
                
                // Show the ssh tunnel setup modal and reroute the next button
                sshTunnelInfoElement.style.display = "block";
                addButton.onclick = function () {
                    animation.style.display = "block;";
                    sshTunnelInfoElement.style.display = "none;";
                    // Run websocket for status updates during rclone config
                    animation_statustext.innerText = "Waiting for connection...";
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
                };
            };
        };
    }
    xhr.send();
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


function getConnections() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/sync/onedrive', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                console.log("Received connections response.");
                const selectElement = document.getElementById('connection_selector_modal');

                // Clear existing options
                selectElement.innerHTML = '';

                responseJSON = JSON.parse(xhr.responseText);
                // Add new options
                responseJSON.forEach(optionText => {
                    const optionElement = document.createElement('option');
                    optionElement.value = optionText + ":";
                    optionElement.textContent = optionText;
                    selectElement.appendChild(optionElement);
                });
            };
        };
    }
    xhr.send();
}


function loadOneDriveDir(back = false) {
    const backbuttondiv = document.getElementById("remoteonedrivebackbutton");
    const loadingAnimation = document.getElementById("waitingAnimationPathMapping");
    const listgroup = document.getElementById('onedrivelistgroup');

    backbuttondiv.style.display = "none";
    loadingAnimation.style.display = "block";
    listgroup.style.display = "none";
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/sync/onedrive-directory', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                jsonResponse = JSON.parse(xhr.responseText);
                console.log("Received " + Object.keys(jsonResponse).length + " items.");

                listgroup.innerHTML = '';
                // Iterate through the JSON and create list-group-items dynamically
                for (const [key, value] of Object.entries(jsonResponse)) {
                    const listItem = document.createElement('a');
                    listItem.href = '#';
                    listItem.classList.add('list-group-item', 'list-group-item-action', 'd-flex', 'justify-content-between', 'align-items-center');

                    const icon = document.createElement('i');
                    icon.classList.add('bi', 'bi-folder');

                    const span = document.createElement('span');
                    span.appendChild(icon);
                    span.appendChild(document.createTextNode(` ${key}`));

                    const arrowIcon = document.createElement('i');
                    arrowIcon.classList.add('bi', 'bi-arrow-return-right');

                    if (value > 0) {
                        listItem.appendChild(span);
                        listItem.appendChild(arrowIcon);
                    } else {
                        listItem.appendChild(span);
                    }


                    // Add event listeners
                    listItem.addEventListener('click', handleRemotePathClick);
                    listItem.addEventListener('dblclick', handleRemotePathDoubleClick);
                    listgroup.appendChild(listItem);
                }
                const backbutton = backbuttondiv.querySelector("button");
                if (onedriveDirLevel === 1) {
                    backbutton.disabled = true;
                } else {
                    backbutton.disabled = false;
                }
                backbuttondiv.style.display = "block";
                loadingAnimation.style.display = "none";
                listgroup.style.display = "block";
            };
        };
    }
    if (back) {
        currentOneDrivePath = currentOneDrivePath.replace(/\/[^/]*\/?$/, '/')
        onedriveDirLevel--;
    }
    xhr.send(JSON.stringify({ "remote_id": document.getElementById("connection_selector_modal").value, "path": currentOneDrivePath }));
}

function handleRemotePathClick(event) {
    const targetItem = event.currentTarget;

    // Remove 'active' class from all items
    onedriveLocalListGroup.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add 'active' class to the clicked item
    targetItem.classList.add('active');

    setCurrentPathRemote(targetItem.textContent);
}

function setCurrentPathRemote(pathToAdd) {
    // Remove space from start and end of path
    pathToAdd = pathToAdd.trim();

    if (currentOneDriveSelectedPath.startsWith("/")) {
        if (currentOneDriveSelectedPath.split("/").length - 2 === onedriveDirLevel) {
            currentOneDriveSelectedPath = updateSameLevel(currentOneDriveSelectedPath, pathToAdd);
        } else if (currentOneDriveSelectedPath.split("/").length - 2 > onedriveDirLevel) {
            currentOneDriveSelectedPath = currentOneDriveSelectedPath.replace(/\/[^/]*\/?$/, '/') // Remove last dir

        } else {
            currentOneDriveSelectedPath = updateDeeperLevel(currentOneDriveSelectedPath, pathToAdd);
        }
    } else {
        currentOneDriveSelectedPath = "/" + pathToAdd + "/";
    }
    document.getElementById("remote_path").value = currentOneDriveSelectedPath;
    evaluatePathMappingSubmitButton();
}

function handleRemotePathDoubleClick(event) {
    const targetItem = event.currentTarget;
    // Test if the inner html of the targetItem contains an icon
    if (targetItem.innerHTML.includes("bi-arrow-return-right")) {
        // If it does, it means the item is a directory, so we can load the directory
        onedriveDirLevel += 1;
        currentOneDrivePath += targetItem.textContent.trim() + "/";
        console.log("User is now in dir: " + currentOneDrivePath);
        loadOneDriveDir();
    }
}

function updateSameLevel(path, newDir) {
    // Remove leading and trailing slashes, then split the path into an array of directories
    const pathArray = path.replace(/^\/|\/$/g, '').split('/');

    // Remove the last element (directory) from the array
    pathArray.pop();

    // Append the new directory to the array
    pathArray.push(newDir);

    // Join the array back into a string with '/' as the separator
    let newPath = '/' + pathArray.join('/') + '/';

    return newPath;
}

function updateDeeperLevel(currentFilePath, newDirectoryName) {
    currentFilePath += newDirectoryName + '/';
    return currentFilePath;
}


function addPathMapping() {
    // Hide form
    const modalbody = document.getElementById("pathmappingmodal_body");
    modalbody.style.display = "none";
    const modalfooter = document.getElementById("pathmappingmodal_footer");
    modalfooter.style.display = "none";

    // Show waiting animation
    const waitingAnimation = document.getElementById("waitingAnimationPathMappingSent");
    waitingAnimation.style.display = "block";

    // Get all relevant elements
    const remotePath = document.getElementById("remote_path").value;
    const localPath = document.getElementById("local_path").value;
    const connection_selector = document.getElementById("connection_selector_modal").value;


    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/sync/pathmapping', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            waitingAnimation.style.display = "none";
            const finalPathMappingStatus = document.getElementById("finalPathMappingStatus");
            const finalPathMappingStatusSuccess = document.getElementById("finalPathMappingStatusSuccess");
            const finalPathMappingStatusFailed = document.getElementById("finalPathMappingStatusError");
            finalPathMappingStatusFailed.style.display = (xhr.status === 200) ? "none" : "block";
            finalPathMappingStatusSuccess.style.display = (xhr.status === 200) ? "block" : "none";
            const finalPathMappingStatusText = document.getElementById("finalPathMappingStatusText");
            finalPathMappingStatusText.innerText = xhr.responseText;
            finalPathMappingStatus.style.display = "block";
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                console.log(xhr.responseText);
                addPathMappingToUI(localPath, remotePath, connection_selector);
            };
        };
    }
    xhr.send(JSON.stringify({ "remote_id": connection_selector, "remote_path": remotePath, "local_path": localPath }));
}

function resetPathMappingModal() {
    const modalbody = document.getElementById("pathmappingmodal_body");
    modalbody.style.display = "block";
    const modalfooter = document.getElementById("pathmappingmodal_footer");
    modalfooter.style.display = "block";
    const waitingAnimation = document.getElementById("waitingAnimationPathMappingSent");
    waitingAnimation.style.display = "none";
    const finalPathMappingStatus = document.getElementById("finalPathMappingStatus");
    finalPathMappingStatus.style.display = "none";
    const local_path = document.getElementById("local_path");
    local_path.value = "";
}


function addPathMappingToUI(local, remote, connection) {
    var newCard = document.createElement('div');
    newCard.classList.add('col');
    newCard.id = local + "_pathmappingcard";
    newCard.innerHTML = `
            <div class="card">
                <div class="card-header">
                    ${local}
                </div>
                <div class="card-body">
                    <ol class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Local</div>
                                <i class="bi bi-folder"></i> ${local}
                            </div>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Remote</div>
                                <i class="bi bi-folder"></i><div id="${local}_remote_pathmapping">${connection + remote}</div>
                            </div>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">Type</div>
                                onedrive
                            </div>
                        </li>
                    </ol>
                </div>
                <div class="card-footer">
                    <button id="${local}_edit_button" onclick="editPathMapping('${local}')"
                        class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#pathmappingmodal"><i class="bi bi-pencil"></i> Edit</button>
                    <button id="${local}_delete_button" onclick="deletePathMapping('${local}')"
                        class="btn btn-danger"><i class="bi bi-trash"></i> Delete</button>
                </div>
            </div>`
    document.getElementById("pathmappingscontainer").appendChild(newCard);
}

function deletePathMapping(id) {
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/sync/pathmapping', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                console.log(xhr.responseText);
                const card = document.getElementById(id + "_pathmappingcard");
                card.style.transition = 'opacity 1.5s';
                card.style.opacity = 0;

                // Remove after fade
                setTimeout(() => {
                    card.remove();
                }, 1500);
            };
        };
    }
    xhr.send(JSON.stringify({ "id": id }));
}

function editPathMapping(id) {
    const local_path = document.getElementById("local_path");
    const remote_path = document.getElementById("remote_path");
    const connection = document.getElementById("connection_selector_modal");

    local_path.value = id;
    remote_path.value = document.getElementById(id + "_remote_pathmapping").innerText.split(":")[1];
    var optionElement = document.createElement('option');
    optionElement.value = document.getElementById(id + "_remote_pathmapping").innerText.split(":")[0] + ":"
    optionElement.textContent = document.getElementById(id + "_remote_pathmapping").innerText.split(":")[0];
    connection.appendChild(optionElement);
}

function deleteFailedSync(id) {
    const xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/sync/failedpdf', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status !== 200) {
                console.error(xhr.responseText);
                alert(xhr.responseText);
            } else {
                console.log(xhr.responseText);
                const row = document.getElementById(id + '_failedpdf_row');
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
    xhr.send(JSON.stringify({ "id": id }));
}

function downloadFailedSync(id) {
    window.open("/sync/failedpdf?download_id=" + id);
}

function copyCommand() {
    var commandElement = document.querySelector('.terminal-command');
    var commandText = commandElement.innerText;

    var textarea = document.createElement('textarea');
    textarea.value = commandText;
    document.body.appendChild(textarea);
    textarea.select();
    textarea.setSelectionRange(0, 99999); // for mobile
    navigator.clipboard.writeText(textarea.value);
    document.body.removeChild(textarea);

    console.log('Command copied to clipboard!');
}
