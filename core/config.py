import os
from pathlib import Path

from dotenv import load_dotenv

# Base directories
SCRIPT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = SCRIPT_DIR / "vpn_configs"
STATE_FILE = SCRIPT_DIR / ".proxy_state.json"

env_file = SCRIPT_DIR / ".env"
dotenv_loaded = load_dotenv(dotenv_path=env_file)

# OpenVPN credentials from environment variables
OPENVPN_USER = os.environ.get("OPENVPN_USER")
OPENVPN_PASS = os.environ.get("OPENVPN_PASS")

# Proxy authentication credentials
# These are the credentials for the 3proxy server itself
PROXY_USER = os.environ.get("PROXY_USER")
PROXY_PASS = os.environ.get("PROXY_PASS")

# REST API settings
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8080"))
API_AUTH_ENABLED = os.environ.get("API_AUTH_ENABLED", "0") == "1"
API_USER = os.environ.get("API_USER")
API_PASS = os.environ.get("API_PASS")
