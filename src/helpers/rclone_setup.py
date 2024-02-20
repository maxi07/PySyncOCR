import pexpect
import re
from src.helpers.logger import logger
from src.helpers.run_subprocess import run_subprocess
from flask import current_app
from src.webserver import socketio


sp_name = None
sp_library = None


def extract_url(prompt):
    # Use regular expression to extract the URL from the prompt
    match = re.search(r'http://[^\s]+', prompt)
    if match:
        return match.group(0)
    return None


def configure_rclone_onedrive_personal(name):
    # Run the rclone config command using pexpect
    process = pexpect.spawn('rclone config')
    logger.info("Configuring OneDrive with rclone, please wait...")
    socketio.emit("message_update", "Connecting to OneDrive...", namespace="/websocket-onedrive")
    socketio.sleep(0.1)
    try:
        # Wait for the initial output and print it
        process.expect("Quit config", timeout=10)
        logger.debug("Started rclone")

        # Send 'n' to create a new remote
        process.sendline('n')
        logger.debug("Selected [n] to create a new remote")

        # Enter the remote name (e.g., 'myonedrive')
        process.expect('name>')
        process.sendline(name)
        logger.debug(f"Set name to {name}")

        # Choose the storage type (e.g., 'onedrive')
        try:
            process.expect('Storage>', timeout=1)
        except pexpect.exceptions.TIMEOUT:
            if "already exists" in process.buffer.decode():
                logger.error("Remote with that name already exists.")
                socketio.emit("message_update", "Remote with that name already exists.", namespace="/websocket-onedrive")
                socketio.sleep(0.1)
            else:
                logger.error(process.buffer.decode())
                socketio.emit("message_update", "Error: " + process.buffer.decode(), namespace="/websocket-onedrive")
                socketio.sleep(0.1)
        process.sendline('onedrive')
        logger.debug("Selected option onedrive")

        # Handle OAuth client ID and secret if needed
        process.expect('client_id>')
        process.sendline('')
        logger.debug("Skipped client_id")
        process.expect('client_secret>')
        process.sendline('')
        logger.debug("Skipped client_secret")

        # Edit advanced config if needed
        process.expect('Edit advanced config?')
        process.sendline('n')
        logger.debug("Selected advanced config: no")

        # Use auto config
        process.expect('Use auto config?')
        process.sendline('y')
        logger.debug("Selected auto config")

        # Wait for the user to open the authorization link in a browser
        process.expect("If your browser doesn't open automatically go to the following link:", timeout=60)
        logger.debug("Received auth prompt.")
        auth_url = extract_url(process.buffer.decode())
        logger.debug(f"Received auth url: {auth_url}")

        if auth_url:
            logger.info("If your browser doesn't open automatically, go to the following link:")
            logger.info(auth_url)
            socketio.emit("message_update", auth_url, namespace="/websocket-onedrive")
            socketio.sleep(0.1)

            # Continue handling prompts
            process.expect('Your choice>', timeout=120)
            process.sendline('1')  # OneDrive Personal or Business
            logger.debug("Selected [1] as OneDrive Personal")

            # Wait for drive selection
            process.expect('drive to use')
            process.sendline('0')  # Choose the first drive (index 0)
            logger.debug("Selected [0] as first drive")

            # Confirm drive selection
            process.expect('Is that okay?')
            process.sendline('y')
            logger.debug("Selected [y] to approve drive selection")

            # Wait for the final output
            process.expect('Yes this is OK')
            process.sendline('y')
            logger.debug("Selected [y] for final confirmation")
            logger.info("Success setting up OneDrive!")
            socketio.emit("message_update", "Success setting up OneDrive!", namespace="/websocket-onedrive")
            socketio.sleep(0.1)
        else:
            logger.error("Failed to extract authorization URL.")
            socketio.emit("message_update", "Failed to extract authorization URL.", namespace="/websocket-onedrive")
            socketio.sleep(0.1)

    except pexpect.EOF:
        logger.error("Error: Unexpected end of input.")
        logger.error(process.before.decode())
        socketio.emit("message_update", "Error: Unexpected end of input.", namespace="/websocket-onedrive")
        socketio.sleep(0.1)

    except Exception:
        logger.error(process.buffer.decode())
        socketio.emit("message_update", process.buffer.decode(), namespace="/websocket-onedrive")
        socketio.sleep(0.1)

    finally:
        # Close the process
        process.close()


def configure_rclone_onedrive_sharepoint(name, sharepoint_name):
    global sp_name, sp_library
    sp_name = None
    sp_library = None
    # Run the rclone config command using pexpect
    process = pexpect.spawn('rclone config')
    logger.info("Configuring OneDrive with rclone for SharePoint, please wait...")
    socketio.emit("message_update", "Connecting to SharePoint...", namespace="/websocket-onedrive")
    socketio.sleep(0.1)
    try:
        # Wait for the initial output and print it
        process.expect("Quit config", timeout=10)
        logger.debug("Started rclone")

        # Send 'n' to create a new remote
        process.sendline('n')
        logger.debug("Selected [n] to create a new remote")

        # Enter the remote name (e.g., 'myonedrive')
        process.expect('name>')
        process.sendline(name)
        logger.debug(f"Set name to {name}")

        # Choose the storage type (e.g., 'onedrive')
        try:
            process.expect('Storage>', timeout=1)
        except pexpect.exceptions.TIMEOUT:
            if "already exists" in process.buffer.decode():
                logger.error("Remote with that name already exists.")
                socketio.emit("message_update", "Remote with that name already exists.", namespace="/websocket-onedrive")
                socketio.sleep(0.1)
            else:
                logger.error(process.buffer.decode())
                socketio.emit("message_update", "Error: " + process.buffer.decode(), namespace="/websocket-onedrive")
                socketio.sleep(0.1)
        process.sendline('onedrive')
        logger.debug("Selected option onedrive")

        # Handle OAuth client ID and secret if needed
        process.expect('client_id>')
        process.sendline('')
        logger.debug("Skipped client_id")
        process.expect('client_secret>')
        process.sendline('')
        logger.debug("Skipped client_secret")

        # Edit advanced config if needed
        process.expect('Edit advanced config?')
        process.sendline('n')
        logger.debug("Selected advanced config: no")

        # Use auto config
        process.expect('Use auto config?')
        process.sendline('y')
        logger.debug("Selected auto config")

        # Wait for the user to open the authorization link in a browser
        process.expect("If your browser doesn't open automatically go to the following link:", timeout=60)
        logger.debug("Received auth prompt.")
        auth_url = extract_url(process.buffer.decode())
        logger.debug(f"Received auth url: {auth_url}")

        if auth_url:
            logger.info("If your browser doesn't open automatically, go to the following link:")
            logger.info(auth_url)
            socketio.emit("message_update", auth_url, namespace="/websocket-onedrive")
            socketio.sleep(0.1)

            # Continue handling prompts
            process.expect('Your choice>', timeout=120)
            socketio.emit("message_update", "Authenticated user successfully.", namespace="/websocket-onedrive")
            socketio.sleep(0.1)
            socketio.emit("message_update", "Selecting SharePoint...", namespace="/websocket-onedrive")
            socketio.sleep(0.1)
            process.sendline('search')
            logger.debug("Selected [5] as SharePoint search")

            # Search the SharePoint
            process.expect('What to search for>')
            process.sendline(sharepoint_name)
            logger.debug(f"Set search to {sharepoint_name}")

            # Select a result
            process.expect('Chose drive to use:>')
            # Handle search results
            search_results_sp = extract_sharepoint_options(process.before)
            sp_message = {"message": "Select a SharePoint", "step": "sp_select", "options": search_results_sp}
            socketio.emit('rclone_sp_update', sp_message, namespace="/websocket-onedrive")

            timeout_spname = 120
            timeout_spname_count = 0
            while sp_name is None:
                socketio.sleep(1)
                timeout_spname_count += 1
                if timeout_spname_count >= timeout_spname:
                    socketio.emit("rclone_sp_update", "Timeout waiting for SharePoint selection.", namespace="/websocket-onedrive")
                    socketio.sleep(0.1)
                    raise Exception("Timeout waiting for SharePoint selection.")

            if int(sp_name) >= 0 and int(sp_name) < (len(search_results_sp)):
                process.sendline(sp_name)
                logger.debug(f"Selected SharePoint {sp_name}")
            else:
                socketio.emit("rclone_sp_update", "Invalid SharePoint selection.", namespace="/websocket-onedrive")
                socketio.sleep(0.1)
                raise Exception("Invalid SharePoint selection.")

            # Select a result for the library
            process.expect('Chose drive to use:>', timeout=120)
            search_results_sp_library = extract_sharepoint_options(process.before)
            sp_message = {"message": "Select a library", "step": "library_select", "options": search_results_sp_library}
            socketio.emit('rclone_sp_update', sp_message, namespace="/websocket-onedrive")
            socketio.sleep(0.1)

            timeout_splib = 120
            timeout_splib_count = 0
            while sp_library is None:
                socketio.sleep(1)
                timeout_splib_count += 1
                if timeout_splib_count >= timeout_splib:
                    socketio.emit("rclone_sp_update", "Timeout waiting for SharePoint selection.", namespace="/websocket-onedrive")
                    socketio.sleep(0.1)
                    raise Exception("Timeout waiting for SharePoint selection.")

            if int(sp_library) >= 0 and int(sp_library) < (len(search_results_sp_library)):
                process.sendline(sp_library)
                logger.debug(f"Selected SharePoint library {sp_library}")
            else:
                socketio.emit("rclone_sp_update", "Invalid SharePoint library selection.", namespace="/websocket-onedrive")
                socketio.sleep(0.1)
                raise Exception("Invalid SharePoint library selection.")

            # Confirm drive selection
            process.expect('Is that okay?', timeout=120)
            process.sendline('y')
            logger.debug("Selected [y] to approve drive selection")

            # Wait for the final output
            process.expect('Yes this is OK')
            process.sendline('y')
            logger.debug("Selected [y] for final confirmation")
            logger.info("Success setting up OneDrive!")
            socketio.emit("message_update", "Success setting up OneDrive!", namespace="/websocket-onedrive")
            socketio.sleep(0.1)

        else:
            logger.error("Failed to extract authorization URL.")
            socketio.emit("message_update", "Error: Failed to extract authorization URL.", namespace="/websocket-onedrive")
            socketio.sleep(0.1)

    except pexpect.EOF:
        logger.error("Error: Unexpected end of input.")
        logger.error(process.before.decode())
        socketio.emit("message_update", f"Error: Unexpected end of input.\n {process.before.decode()}", namespace="/websocket-onedrive")
        socketio.sleep(0.1)

    except Exception as ex:
        logger.exception(ex)
        logger.error(process.buffer.decode())
        if "returned no results" in process.before.decode():
            logger.error("Error: Invalid SharePoint name.")
            socketio.emit("message_update", "Error: Invalid SharePoint name.", namespace="/websocket-onedrive")
            socketio.sleep(0.1)
        else:
            logger.error("Error: " + process.buffer.decode() + "\n" + process.before.decode())
            socketio.emit("message_update", "Error: " + process.buffer.decode() + "\n" + process.before.decode(), namespace="/websocket-onedrive")
            socketio.sleep(0.1)

    finally:
        # Close the process
        process.close()
        sp_name = None
        sp_library = None


def extract_sharepoint_options(input: bytes) -> list[str]:
    try:
        search_results_sp = []

        # Convert bytes to string and split by '\r\n'
        out_str = input.decode('utf-8')
        lines = out_str.split('\r\n')

        # Iterate through each line starting from index 1 (skip the first line)
        for line in lines[2:]:
            # Extract the site name and URL
            start_index = line.find(':') + 2
            end_index = line.find(')') + 1
            site_info = line[start_index:end_index]
            if site_info:  # Check if site_info is not an empty string
                search_results_sp.append(site_info)
        return search_results_sp
    except Exception as ex:
        logger.exception(f"Failed extracting rclone results: {ex}")
        logger.error(input.decode())
        return []


def check_ssh_enabled():
    logger.info("Checking for ssh service...")
    logger.warning("!!!!!!!!!!!!!!!!!!! REMOVE ME !!!!!!!!!!!!!!!!!!!!!!!!!")
    return 0

    if current_app.debug:
        logger.warning("This is a workaround for debugging purpose. Skipping ssh check.")
        return 0

    # First check if ssh is installed
    command = ['ssh', '-V']
    code, msg = run_subprocess(command)
    if code == 0:
        logger.debug("SSH is installed")
    else:
        logger.warning("SSH is not installed")
        return -1

    # Next, check if ssh is active and running
    command = ['systemctl', 'is-active', 'ssh']
    code, msg = run_subprocess(command)
    if code == 0 and msg == "active":
        logger.debug("SSH is active")
    else:
        logger.warning("SSH is not active")
        return -2

    # Finally, check if ssh is enabled
    command = ['systemctl', 'is-enabled', 'ssh']
    code, msg = run_subprocess(command)
    if code == 0 and msg == "enabled":
        logger.debug("SSH is enabled")
    else:
        logger.warning("SSH is not enabled")
        return -3

    logger.info("SSH is enabled and active")
    return 0


logger.debug(f"Loaded {__name__} module")
