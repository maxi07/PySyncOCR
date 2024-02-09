import subprocess
import os
from src.helpers.logger import logger
from src.helpers.config import config


class SambaController:
    def __init__(self):
        pass

    def start_server(self):
        try:
            command = ["sudo", "systemctl", "start", "smbd"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            logger.info("Samba server started.")

            command = ["sudo", "ufw", "allow", "samba"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            logger.info("Added Samba port to firewall.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error starting Samba server: {e}")

    def stop_server(self):
        try:
            logger.info("Stopping Samba server...")
            command = ["sudo", "systemctl", "stop", "smbd"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            logger.info("Samba server stopped.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error stopping Samba server: {e}")

    def restart_server(self):
        try:
            command = ["sudo", "systemctl", "restart", "smbd"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            logger.info("Samba server restarted.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error restarting Samba server: {e}")

    def add_share_config(self, share_name, path, comment="PySyncOCR Share", require_authentication=True):
        try:
            if not os.path.exists(config.get_filepath("smb_service.share_path")):
                os.mkdir(config.get_filepath("smb_service.share_path"), mode=777)
                logger.info(f"Created directory {config.get_filepath('smb_server.share_path')}")

                # Set owner of folder to user "ocr"
                command = ["sudo", "chown", "ocr:ocr", config.get_filepath("smb_service.share_path")]
                logger.debug(f"Calling {' '.join(command)}")
                res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                logger.debug(f"Received {res}")
                logger.info(f"Set owner of {config.get_filepath('smb_service.share_path')} to user ocr.")

                # Set permissions of folder to user "ocr"
                command = ["sudo", "chmod", "777", config.get_filepath("smb_service.share_path")]
                logger.debug(f"Calling {' '.join(command)}")
                res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                logger.debug(f"Received {res}")
                logger.info(f"Set permissions of {config.get_filepath('smb_service.share_path')} to user ocr.")
            else:
                logger.debug(f"Directory {config.get_filepath('smb_service.share_path')} already exists.")
        except Exception as e:
            logger.exception(f"Error creating directory: {e}")
            return

        try:
            with open('/etc/samba/smb.conf', 'a') as smb_conf:
                smb_conf.write(f"\n[{share_name}]\n")
                smb_conf.write(f"path = {path}\n")
                smb_conf.write(f"comment = {comment}\n")
                if require_authentication:
                    smb_conf.write("valid users = ocr\n")
                    smb_conf.write("guest ok = no\n")
                else:
                    smb_conf.write("guest ok = yes\n")
                    smb_conf.write("public = yes\n")
                smb_conf.write("writable = yes\n")
                smb_conf.write("browsable = yes\n")
                logger.info(f"Added Samba share configuration for {share_name}.")
        except Exception as e:
            logger.exception(f"Error adding Samba share configuration: {e}")

    def add_user(self, username, password):
        try:
            command = ["sudo", "useradd", username]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
        except subprocess.CalledProcessError as e:
            if e.returncode == 9:
                logger.warning(f"User {username} already exists.")
            else:
                logger.exception(f"Error adding user to Samba: {e}")
                return

        # Run sudo smbpasswd -a username
        try:
            process = subprocess.Popen(["sudo", "smbpasswd", "-a", username],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True)

            # Provide password as input
            stdout, stderr = process.communicate(input=password + '\n' + password + '\n')
            # Check if any error occurred
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)
            else:
                logger.info(f"Added user {username} to Samba.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error adding user to Samba: {e}")

    def delete_user(self, username):
        try:
            command = ["sudo", "userdel", "-r", username]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            logger.info(f"User {username} deleted from Samba.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error deleting user from Samba: {e}")

    def check_share_exists(self, share_name):
        try:
            logger.debug(f"Checking if Samba share {share_name} exists.")
            with open('/etc/samba/smb.conf', 'r') as smb_conf:
                for line in smb_conf:
                    if line.strip().startswith(f"[{share_name}]"):
                        logger.debug(f"Share {share_name} exists.")
                        return True
            logger.debug(f"Share {share_name} does not exist.")
            return False
        except Exception as e:
            logger.exception(f"Error checking Samba share: {e}")
            return False

    def check_is_running() -> bool:
        try:
            command = ["sudo", "systemctl", "is-active", "smbd"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            if res.stdout.decode() == "active":
                return True
            return False
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error checking Samba server status: {e}")
            return False

    def get_status_message() -> str:
        try:
            command = ["sudo", "systemctl", "show", "-p", "StatusText", "smbd"]
            logger.debug(f"Calling {' '.join(command)}")
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.debug(f"Received {res}")
            return res.stdout.decode().split("=")[1].strip()
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error checking Samba server status: {e}")
            return "Unknown"
