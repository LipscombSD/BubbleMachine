import requests
import logging
import hashlib
from app import settings

logger = logging.getLogger(__name__)


def is_real_ip(ip: str):
    """
    Check if the given IP address is legitimate (not a proxy or VPN).

    Args:
        ip (str): The IP address to check.

    Returns:
        bool: True if the IP is not a proxy, False otherwise.
    """
    api_key = settings.PROXYCHECK_API_KEY
    url = f'http://proxycheck.io/v2/{ip}?key={api_key}'
    logger.info(f'url: {url}')

    try:
        response = requests.get(url)
        logger.info(f'response: {response.json()}')
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'ok':
            # The IP is the key in the ProxyCheck API response
            ip_data = data.get(ip, {})
            return ip_data.get('proxy') == 'no'
    except Exception as e:
        logger.error(f"Error checking IP {ip}: {e}")
        return False  # Default to not allowing if API fails
    return False


def generate_fingerprint(ip, user_agent, email_domain):
    """Generate unique fingerprint to track user registration."""
    data = f"{ip}{user_agent}{email_domain}"
    return hashlib.sha256(data.encode()).hexdigest()