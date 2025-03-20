import os
from typing import Any

from dotenv import dotenv_values

config = {
    **dotenv_values(f".env"),  # load shared development variables
    **dotenv_values(f".env.shared"),  # load shared development variables
    **dotenv_values(f".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

def load_requests_proxies() -> dict[str, Any]:
    http_proxy = None
    https_proxy = None
    if 'http_proxy' in config:
        http_proxy = config['http_proxy']
    if 'https_proxy' in config:
        https_proxy = config['https_proxy']
    if http_proxy or https_proxy:
        proxies = {}
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        return proxies
    return None