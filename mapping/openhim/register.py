import requests
import json
import logging
import time
from django.conf import settings
from .config import get_mediator_metadata, get_client_metadata

logger = logging.getLogger(__name__)

def wait_for_openhim(url, verify_ssl, timeout=60):
    """Wait for OpenHIM Management API to be responsive."""
    heartbeat_url = f"{url}/heartbeat"
    start_time = time.time()
    logger.info(f"Waiting for OpenHIM at {heartbeat_url}...")
    while time.time() - start_time < timeout:
        try:
            response = requests.get(heartbeat_url, verify=verify_ssl, timeout=2)
            if response.status_code == 200:
                logger.info("OpenHIM is responsive.")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(5)
    logger.warning("OpenHIM did not become responsive within timeout.")
    return False

def setup_openhim_channel(openhim_url, username, password, verify_ssl):
    """
    Creates the OpenHIM channel if it doesn't already exist.
    """
    metadata = get_mediator_metadata()
    channels_url = f"{openhim_url}/channels"
    
    # Extract channel config from metadata
    if 'defaultChannelConfig' not in metadata or not metadata['defaultChannelConfig']:
        logger.info("No default channel configuration found in metadata.")
        return
    
    channel_config = metadata['defaultChannelConfig'][0]
    
    try:
        # Check if channel exists
        response = requests.get(
            channels_url,
            auth=(username, password),
            verify=verify_ssl,
            timeout=10
        )
        
        if response.status_code == 200:
            existing_channels = response.json()
            for channel in existing_channels:
                if channel.get('name') == channel_config.get('name'):
                    logger.info(f"Channel '{channel_config.get('name')}' already exists. Updating configuration...")
                    channel_id = channel.get('_id')
                    update_url = f"{channels_url}/{channel_id}"
                    response = requests.put(
                        update_url,
                        json=channel_config,
                        auth=(username, password),
                        verify=verify_ssl,
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        logger.info(f"Successfully updated channel: {channel_config.get('name')}")
                    else:
                        logger.warning(f"Failed to update channel (Status {response.status_code}): {response.text}")
                    return
        
        # Create channel
        logger.info(f"Creating OpenHIM channel: {channel_config.get('name')}...")
        response = requests.post(
            channels_url,
            json=channel_config,
            auth=(username, password),
            verify=verify_ssl,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully created channel: {channel_config.get('name')}")
        else:
            logger.warning(f"Failed to create channel (Status {response.status_code}): {response.text}")
            
    except Exception as e:
        logger.error(f"Error setting up OpenHIM channel: {e}")

def setup_openhim_client(openhim_url, username, password, verify_ssl):
    """
    Creates the OpenHIM client if it doesn't already exist.
    """
    client_metadata = get_client_metadata()
    clients_url = f"{openhim_url}/clients"
    
    try:
        # Check if client exists
        response = requests.get(
            f"{clients_url}/{client_metadata['urn']}",
            auth=(username, password),
            verify=verify_ssl,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Client '{client_metadata['urn']}' already exists.")
            return True
        
        # Create client
        logger.info(f"Creating OpenHIM client: {client_metadata['urn']}...")
        response = requests.post(
            clients_url,
            json=client_metadata,
            auth=(username, password),
            verify=verify_ssl,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully created client: {client_metadata['urn']}")
            return True
        else:
            logger.warning(f"Failed to create client (Status {response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up OpenHIM client: {e}")
        return False

def register_mediator(max_retries=12, retry_delay=10):
    """
    Registers the mediator with the OpenHIM Core with retries.
    """
    openhim_url = getattr(settings, 'OPENHIM_URL', 'http://openhim-core:5001')
    username = getattr(settings, 'OPENHIM_API_USERNAME', 'root@openhim.org')
    password = getattr(settings, 'OPENHIM_API_PASSWORD', 'openhim-password')
    verify_ssl = getattr(settings, 'VERIFY_SSL', True)
    
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    url = f"{openhim_url}/mediators"
    metadata = get_mediator_metadata()
    
    logger.info(f"Attempting to register mediator with OpenHIM at {url}...")
    
    if not wait_for_openhim(openhim_url, verify_ssl):
        logger.error("Skipping registration: OpenHIM is not reachable.")
        return False

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                url, 
                json=metadata, 
                auth=(username, password),
                timeout=60,
                verify=verify_ssl
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully registered mediator with OpenHIM.")
                # After successful registration, setup the client and channel
                setup_openhim_client(openhim_url, username, password, verify_ssl)
                setup_openhim_channel(openhim_url, username, password, verify_ssl)
                return True
            else:
                logger.warning(f"Attempt {attempt}/{max_retries}: Failed to register mediator (Status {response.status_code}).")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt}/{max_retries}: Could not connect to OpenHIM ({e}).")
            
        if attempt < max_retries:
            time.sleep(retry_delay)
    
    logger.error("Max retries reached. Mediator registration failed.")
    return False
