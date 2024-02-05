import subprocess
from src.helpers.logger import logger


class SambaController:
    def __init__(self):
        pass

    def start_server(self):
        try:
            subprocess.run(["systemctl", "start", "smbd"], check=True)
            logger.info("Samba server started.")
            subprocess.run(["ufw", "allow", "samba"], check=True)
            logger.info("Added Samba port to firewall.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error starting Samba server: {e}")

    def stop_server(self):
        try:
            logger.debug("Stopping Samba server...")
            subprocess.run(["systemctl", "stop", "smbd"], check=True)
            logger.info("Samba server stopped.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error stopping Samba server: {e}")

    def restart_server(self):
        try:
            subprocess.run(["systemctl", "restart", "smbd"], check=True)
            logger.info("Samba server restarted.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error restarting Samba server: {e}")

    def add_share_config(self, share_name, path, comment="PySyncOCR Share", require_authentication=True):
        try:
            with open('/etc/samba/smb.conf', 'a') as smb_conf:
                smb_conf.write(f"\n[{share_name}]\n")
                smb_conf.write(f"path = {path}\n")
                smb_conf.write(f"comment = {comment}\n")
                if require_authentication:
                    smb_conf.write("valid users = @smbusers\n")
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
            subprocess.run(["useradd", username], check=True)
        except subprocess.CalledProcessError as e:
            if e.returncode == 9:
                logger.warning(f"User {username} already exists.")
            else:
                logger.exception(f"Error adding user to Samba: {e}")
                return

        # Run sudo smbpasswd -a username
        try:
            process = subprocess.Popen(["smbpasswd", "-a", username],
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
            subprocess.run(["userdel", "-r", username], check=True)
            logger.info(f"User {username} deleted from Samba.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error deleting user from Samba: {e}")

    def check_share_exists(self, share_name):
        try:
            with open('/etc/samba/smb.conf', 'r') as smb_conf:
                for line in smb_conf:
                    if line.strip().startswith(f"[{share_name}]"):
                        return True
            return False
        except Exception as e:
            logger.exception(f"Error checking Samba share: {e}")
            return False

    def check_is_running() -> bool:
        try:
            res = subprocess.run(["systemctl", "is-active", "smbd"], check=True)
            if res == "active":
                return True
            return False
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error checking Samba server status: {e}")
            return False


# Example usage
# samba_controller = SambaController()
# samba_controller.start_server()
# samba_controller.configure_server(guest=False, credentials=('user1', 'password1'))
# samba_controller.add_user('user1', 'password1')
# samba_controller.stop_server()
