function toggle_filename_switch() {
    const filename_switch = document.getElementById("filenamesswitch");
    const filename_label = document.getElementById("filenamesswitch_label");

    filename_label.innerText = "Automatic file names are " + (filename_switch.checked ? "enabled" : "disabled");
}
