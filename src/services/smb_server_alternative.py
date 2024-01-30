import subprocess
from src.helpers.logger import logger


class SambaController:
    def __init__(self):
        pass

    def start_server(self):
        try:
            subprocess.run(["sudo", "systemctl", "start", "smbd"], check=True)
            logger.info("Samba server started.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error starting Samba server: {e}")

    def stop_server(self):
        try:
            subprocess.run(["sudo", "systemctl", "stop", "smbd"], check=True)
            logger.info("Samba server stopped.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error stopping Samba server: {e}")

    def restart_server(self):
        try:
            subprocess.run(["sudo", "systemctl", "restart", "smbd"], check=True)
            logger.info("Samba server restarted.")
        except subprocess.CalledProcessError as e:
            print(f"Error restarting Samba server: {e}")

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
                logger.info(f"Added Samba share configuration for {share_name}.")
        except Exception as e:
            print("Error adding Samba share configuration:", e)

    def add_user(self, username, password):
        try:
            subprocess.run(["sudo", "useradd", username], check=True)
            subprocess.run(["sudo", "smbpasswd", "-a", username], input=password.encode(), check=True)
            logger.info(f"User {username} added to Samba.")
        except subprocess.CalledProcessError as e:
            logger.exception(f"Error adding user to Samba: {e}")

    def delete_user(self, username):
        try:
            subprocess.run(["sudo", "userdel", "-r", username], check=True)
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


# Example usage
# samba_controller = SambaController()
# samba_controller.start_server()
# samba_controller.configure_server(guest=False, credentials=('user1', 'password1'))
# samba_controller.add_user('user1', 'password1')
# samba_controller.stop_server()
