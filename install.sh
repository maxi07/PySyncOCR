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
LOG_FILE="$APP_DIR/install_log.txt"

# Function to log messages
log_message() {
    echo "[ $(date '+%Y-%m-%d %H:%M:%S') ] $1" | tee -a "$LOG_FILE"
}

# Function to log errors and exit
log_error_and_exit() {
    log_message "Error: $1"
    exit 1
}

# Install Python (if not already installed)
log_message "Installing Python..."
sudo apt-get update || log_error_and_exit "Failed to update package lists."
sudo apt-get install -y python3 || log_error_and_exit "Failed to install Python."
sudo apt-get install -y python3-venv || log_error_and_exit "Failed to install Python virtual environment."
sudo apt-get install -y python3-pip || log_error_and_exit "Failed to install Python package manager."
sudo apt-get install -y ocrmypdf || log_error_and_exit "Failed to install OCRmyPDF."
sudo apt-get install -y tesseract-ocr || log_error_and_exit "Failed to install Tesseract OCR."
sudo apt-get install -y tesseract-ocr-deu || log_error_and_exit "Failed to install Tesseract OCR for German language."
sudo apt-get install -y tesseract-ocr-eng || log_error_and_exit "Failed to install Tesseract OCR for English language."
sudo apt-get install -y rclone || log_error_and_exit "Failed to install Rclone."
sudo apt-get install -y autotools-dev || log_error_and_exit "Failed to install AutoTools."
sudo apt-get install -y automake || log_error_and_exit "Failed to install AutoMake."
sudo apt-get install -y libtool || log_error_and_exit "Failed to install LibTool."
sudo apt-get install -y libleptonica-dev || log_error_and_exit "Failed to install LibLeptonica."
sudo apt-get install -y samba || log_error_and_exit "Failed to install Samba."
sudo ./src/helpers/install_jbig2.sh || log_error_and_exit "Failed to install JBIG2."

# Get the current user and group
USERNAME=$(whoami)
GROUP=$(id -gn)

# Set up virtual environment
log_message "Setting up virtual environment..."
python3 -m venv "$VENV_DIR" || log_error_and_exit "Failed to create virtual environment."

# Activate virtual environment
source "$VENV_DIR/bin/activate" || log_error_and_exit "Failed to activate virtual environment."

# Install dependencies
log_message "Installing dependencies..."
pip install -r requirements.txt || log_error_and_exit "Failed to install dependencies."

log_message "Initializing database..."
flask --app src/webserver init-db || log_error_and_exit "Failed to initialize database."

# Create systemd service file
log_message "Creating systemd service file..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
sudo sh -c "cat > $SERVICE_FILE" <<EOF || log_error_and_exit "Failed to create systemd service file."
[Unit]
Description=PySyncOCR
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/python $MAIN_FILE
WorkingDirectory=$APP_DIR
Restart=always
User=$USERNAME
Group=$GROUP

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
log_message "Enabling and starting the service..."
sudo systemctl enable "$SERVICE_NAME.service" || log_error_and_exit "Failed to enable service."
sudo systemctl start "$SERVICE_NAME.service" || log_error_and_exit "Failed to start service."

# Check service status
log_message "Checking service status..."
sudo systemctl status "$SERVICE_NAME.service" || log_error_and_exit "Failed to get service status."

# Check if the service is running
if sudo systemctl is-active --quiet "$SERVICE_NAME.service"; then
    log_message "Service is running."
else
    log_message "Service failed to start."
fi

echo "Installation complete. Log file: $LOG_FILE"
