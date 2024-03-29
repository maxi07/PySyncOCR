#!/bin/bash

# Check if script is run with sudo
# if [ "$(id -u)" != "0" ]; then
#    echo "This script must be run with sudo." 1>&2
#    exit 1
#fi

# Set the paths and configurations
APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/.venv"
MAIN_FILE="$APP_DIR/main.py"
SERVICE_NAME="PySyncOCR"
DB_FILE="$APP_DIR/instance/pysyncocr.sqlite"
STARTING_DIR="$(pwd)"
INSTALL_SERVICE=true
LOG_FILE="$APP_DIR/install_log.txt"
INSTALL_SERVICE=true
SKIP_PIP=false


for arg in "$@"; do
    case $arg in
        --install-service=FALSE)
            INSTALL_SERVICE=false
            ;;
        --skip-pip=TRUE)
            SKIP_PIP=true
            ;;
    esac
done

# Function to log messages
log_message() {
    echo "[ $(date '+%Y-%m-%d %H:%M:%S') ] $1" | sudo tee -a "$LOG_FILE"
}

# Function to log errors and exit
log_error_and_exit() {
    log_message "Error: $1"
    exit 1
}

install_jbig2() {
    git clone https://github.com/agl/jbig2enc || log_error_and_exit "Failed to download JBIG2."
    cd jbig2enc || log_error_and_exit "Failed to enter JBIG2 directory."
    echo "New working dir: ${PWD}"
    sed -i '1iAC_CONFIG_AUX_DIR(.)' configure.ac || log_error_and_exit "Failed to modify configure.ac."
    ./autogen.sh || log_error_and_exit "Failed to run autogen.sh."
    ./configure && make || log_error_and_exit "Failed to configure and make JBIG2."
    sudo make install || log_error_and_exit "Failed to install JBIG2."
}


# Install Packages (if not already installed)
log_message "Installing Packages..."
sudo apt-get update && apt-get install -y --no-install-recommends python3 python3-venv python3-pip zlib1g-dev openssh-server ocrmypdf tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng pngquant rclone autotools-dev automake autoconf libtool libtool libleptonica-dev samba make g++ build-essential || log_error_and_exit "Failed to install Python and other dependencies."

# Install JBIG2 (if not already installed)
if jbig2 --version >/dev/null 2>&1; then
    log_message "JBIG2 already installed."
else
    log_message "Installing JBIG2..."
    install_jbig2
    cd "$STARTING_DIR" || log_error_and_exit "Failed to return to starting directory."
fi

# Get the current user and group
USERNAME=$(whoami)
GROUP=$(id -gn)

# Set up virtual environment
log_message "Setting up virtual environment..."
python3 -m venv "$VENV_DIR" || log_error_and_exit "Failed to create virtual environment."

# Activate virtual environment
source "$VENV_DIR/bin/activate" || log_error_and_exit "Failed to activate virtual environment."

# Install dependencies if flag is not set to skip
if [ "$SKIP_PIP" = false ]; then
    log_message "Installing dependencies..."
    pip install -r requirements.txt || log_error_and_exit "Failed to install dependencies."
else
    log_message "Skipping pip requirements installation."
fi


log_message "Initializing database..."
# Check if database already exists
if [ -f "$DB_FILE" ]; then
    log_message "Database already exists."
    # Ask to overwrite database
    read -p "Do you want to overwrite the existing database? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Delete existing database
        log_message "Deleting existing database..."
        rm "$DB_FILE" || log_error_and_exit "Failed to delete existing database."
        log_message "Existing database deleted."
    fi
else
    log_message "Database does not exist."
    # Create database
    log_message "Creating database..."
    flask --app src/webserver init-db || log_error_and_exit "Failed to initialize database."
    log_message "Database created."
fi


if [ "$INSTALL_SERVICE" = true ]; then
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
else
    log_message "Skipping service installation."
fi

echo ""
echo ""
echo "=========================================="
echo "Installation complete. Log file: $LOG_FILE"
echo ""
echo "Access the webui via http://$(hostname):5000"
echo "=========================================="
