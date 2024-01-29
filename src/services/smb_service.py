from impacket import smbserver
from src.helpers.logger import logger
from impacket.ntlm import compute_lmhash, compute_nthash


class MySMBServer():
    def __init__(self, settings):
        logger.info("Initializing SMB server...")

        try:
            self.server = smbserver.SimpleSMBServer("127.0.0.1")
        except PermissionError:
            logger.error("Cannot start SMB server. Please run the script with appropriate privileges (e.g., use sudo)")
            return

        self.settings = settings
        logger.debug(f"Received SMB settings: {self.settings}")

        try:
            self.server.addShare(settings["share_name"].upper(), settings["share_path"], "PySyncOCR Share")
            self.server.setSMB2Support(True)
            lmhash = compute_lmhash(settings["password"])
            nthash = compute_nthash(settings["password"])
            self.server.addCredential(settings["username"], 0, lmhash, nthash)
            self.isInitialized = True
            logger.info("Finished setting up SMB Server")
        except Exception as e:
            logger.error(f"Error during SMB server setup: {e}")
            self.isInitialized = False

    def onSessionStart(self, session):
        # You can add custom logic when a new session starts
        logger.info(f"New session started: {session.get_client_name()}")

    def start(self):
        if self.isInitialized:
            logger.info("Started SMB service")
            self.server.start()
        else:
            logger.error("Cannot start SMB server as initialization is missing.")


logger.debug(f"Loaded {__name__} module")
