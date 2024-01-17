data = [
    "Anlagen/",
    "AppData/",
    "Apps/",
    "Aufnahmen/",
    "Besprechungen/",
    "Bilder/",
    "Creative Cloud Files/",
    "Desktop/",
    "Dokumente/",
    "E-Mail-Anlagen/",
    "Microsoft Edge Downloads/",
    "Microsoft Teams Chat Files/",
    "Microsoft Teams Data/",
    "Microsoft Teams-Chatdateien/",
    "Notizbücher/",
    "Whiteboards/",
    "leer/",
    "test2/",
    "Bilder/AnyDesk/",
    "Bilder/CameraHub/",
    "Bilder/Catalyst Browse/",
    "Bilder/Eigene Aufnahmen/",
    "Bilder/Livestream Studio/",
    "Bilder/Saved Pictures/",
    "Bilder/Screenshots/",
    "Bilder/Videoprojekte/",
    "Bilder/fa_icons/",
    "Bilder/iCloud Photos/",
    "AppData/Roaming/",
    "Apps/Microsoft Edge/",
    "Apps/Microsoft Forms/",
    "Creative Cloud Files/SVG/",
    "Microsoft Teams Data/Wiki/",
    "Dokumente/Admin/",
    "Dokumente/Adobe/",
    "Dokumente/Advanced Installer/",
    "Dokumente/Audioaufzeichnungen/",
    "Dokumente/AutoHotkey/",
    "Dokumente/Backup/",
    "Dokumente/Benutzerdefinierte Office-Vorlagen/",
    "Dokumente/Citavi 6/",
    "Dokumente/Coding Backup/",
    "Dokumente/Drivelist_Dokumente/",
    "Dokumente/EVE/",
    "Dokumente/Fax/",
    "Dokumente/Fresenius/",
    "Dokumente/Grafiken/",
    "Dokumente/IISExpress/",
    "Dokumente/MAXQDA2022/",
    "Dokumente/MAXQDA2022 Reader/",
    "Dokumente/MAXQDA_Externals/",
    "Dokumente/MBS/",
    "Dokumente/MDMlogs/",
    "Dokumente/Meine Datenquellen/",
    "Dokumente/My Web Sites/",
    "Dokumente/New-Project/",
    "Dokumente/OneNote-Notizbücher/",
    "Dokumente/Outlook-Dateien/",
    "Dokumente/PAGES/",
    "Dokumente/PlatformIO/",
    "Dokumente/PowerToys/",
    "Dokumente/Privat/",
    "Dokumente/Red Giant/",
    "Dokumente/Scanned Documents/",
    "Dokumente/Soundaufnahmen/",
    "Dokumente/VideoCopilot/",
    "Dokumente/Visual Studio 2019/",
    "Dokumente/Visual Studio 2022/",
    "Dokumente/WPA Files/",
    "Dokumente/Wichtig/",
    "Dokumente/WindowsPowerShell/",
    "Dokumente/Zoom/",
    "Whiteboards/Annotations/"
]

# Convert the list into a dictionary
directory_dict = {}

for item in data:
    parts = item.split("/")
    top_level_directory = parts[0]
    
    if top_level_directory not in directory_dict:
        directory_dict[top_level_directory] = 0
    else:
        directory_dict[top_level_directory] += 1

# Print the resulting dictionary
print(directory_dict)
