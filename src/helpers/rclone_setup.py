import pexpect
import re
from src.helpers.logger import logger


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
                return -2
            else:
                logger.error(process.buffer.decode())
                return -1
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
            yield auth_url

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
            yield "0"
        else:
            logger.error("Failed to extract authorization URL.")
            return -3

    except pexpect.EOF:
        logger.error("Error: Unexpected end of input.")
        logger.error(process.before.decode())
        return -4

    except Exception:
        logger.error(process.buffer.decode())
        return -5

    finally:
        # Close the process
        process.close()


logger.debug(f"Loaded {__name__} module")
