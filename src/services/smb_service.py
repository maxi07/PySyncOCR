from impacket import smbserver
from src.helpers.logger import logger
from impacket.ntlm import compute_lmhash, compute_nthash
import sys
import threading


class MySMBServer():
    def __init__(self, settings, port=445):
        logger.info("Initializing SMB server...")
        self._stop_event = threading.Event()
        try:
            self.server = smbserver.SimpleSMBServer("127.0.0.1", listenPort=port)
        except PermissionError:
            logger.error("Cannot start SMB server. Please run the script with appropriate privileges (e.g., use sudo)")
            return
        except OSError as oser:
            if oser.errno == 98:
                logger.error("Cannot start SMB server as there already is one running.")
                logger.error("Please use the --smb-port option to specify a different port.")
                sys.exit(98)

        self.settings = settings
        logger.debug(f"Received SMB settings: {self.settings}")

        try:
            self.server.addShare(settings["share_name"].upper(), settings["share_path"], "PySyncOCR Share")
            self.server.setSMB2Support(True)
            lmhash = compute_lmhash(settings["password"])
            nthash = compute_nthash(settings["password"])
            self.server.addCredential(settings["username"], 0, lmhash, nthash)
            self.isInitialized = True
            self.isRunning = False
            logger.info("Finished setting up SMB Server")
        except Exception as e:
            logger.error(f"Error during SMB server setup: {e}")
            self.isInitialized = False

    def onSessionStart(self, session):
        # You can add custom logic when a new session starts
        logger.info(f"New session started: {session.get_client_name()}")

    def start(self):
        if self.isInitialized:
            self.isRunning = True
            logger.info("Started SMB service")
            self.server.start()
        else:
            logger.error("Cannot start SMB server as initialization is missing.")

    def stop(self):
        if self.isRunning:
            logger.debug("Stopping SMB service...")
            self.server.stop()
            logger.info("Stopped SMB service")
            self.isRunning = False
            self._stop_event.set()
        else:
            logger.warning("SMB server is not running.")

    def is_stopped(self):
        return self._stop_event.is_set()


logger.debug(f"Loaded {__name__} module")
