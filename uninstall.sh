#!/bin/bash

# Check if script is run with sudo
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run with sudo." 1>&2
    exit 1
fi

# Set the paths and configurations
APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/.venv"
MAIN_FILE="$APP_DIR/main.py"
SERVICE_NAME="PySyncOCR"

# Log file
LOG_FILE="$APP_DIR/uninstall_log.txt"

# Function to log messages
log_message() {
    echo "[ $(date '+%Y-%m-%d %H:%M:%S') ] $1" | tee -a "$LOG_FILE"
}

# Function to log errors and exit
log_error_and_exit() {
    log_message "Error: $1"
    exit 1
}

# Stop and disable the service
log_message "Stopping and disabling the service..."
sudo systemctl stop "$SERVICE_NAME.service" || log_error_and_exit "Failed to stop service."
sudo systemctl disable "$SERVICE_NAME.service" || log_error_and_exit "Failed to disable service."

# Remove the service file
log_message "Removing systemd service file..."
sudo rm "/etc/systemd/system/$SERVICE_NAME.service" || log_error_and_exit "Failed to remove service file."

# Deactivate and remove the virtual environment
log_message "Deactivating and removing virtual environment..."
deactivate
rm -rf "$VENV_DIR" || log_error_and_exit "Failed to remove virtual environment."

# Uninstall dependencies installed with apt-get
log_message "Uninstalling dependencies installed with apt-get..."
sudo apt-get remove --purge -y ocrmypdf tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng autotools-dev automake libtool libleptonica-dev || log_error_and_exit "Failed to uninstall dependencies."

# Remove jbig2enc
log_message "Removing jbig2enc..."
cd "$APP_DIR"
sudo rm -rf jbig2enc || log_error_and_exit "Failed to remove jbig2enc."

echo "Uninstallation complete. Log file: $LOG_FILE"