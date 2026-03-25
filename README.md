# ProxyForFree 🆓

ProxyForFree is a tool designed to easily set up multiple **100% free proxy servers** using Proton VPN free config files (`.ovpn`), OpenVPN, and 3proxy. It allows you to route proxy traffic through different VPN tunnels, effectively giving you multiple outgoing IP addresses on a single server without any subscription costs.

---

## Goal
The goal of this project is to provide a simple, **cost-free** way to manage multiple parallel proxy servers, each connected to a different VPN location using Proton VPN's free tier, making it easy to interact with them for testing or scraping purposes.

---

## Live Demo
Usage Example:
```bash
curl -x http://demo_user:deMo_Passw0rd@178.128.207.142:8015 http://ipinfo.io/
```
Simply change the port to switch to a different proxy.

| Proxy                                               | Country      |
|-----------------------------------------------------|--------------|
| http://demo_user:deMo_Passw0rd@178.128.207.142:8012 | 🇺🇸 USA         |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8013 | 🇨🇦 Canada      |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8014 | 🇯🇵 Japan       |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8015 | 🇳🇱 Netherlands |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8016 | 🇷🇴 Romania     |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8017 | 🇸🇬 Singapore   |
| http://demo_user:deMo_Passw0rd@178.128.207.142:8018 | 🇲🇽 Mexico      |

---

## Tech Stack
- **OpenVPN**: Used to establish VPN connections.
- **3proxy**: A tiny but powerful proxy server used to route traffic.
- **Python**: The core management script.
- **FastAPI**: REST API for programmatic proxy management.
- **uv**: Modern Python package manager.

---

## System Requirements
You need a Linux server (Ubuntu/Debian recommended) with root access. You can use free-tier servers from AWS, Oracle Cloud, DigitalOcean, or any other provider for testing.

### 1. Install OpenVPN
```bash
sudo apt-get update
sudo apt-get install openvpn
```

### 2. Install Build Essentials & Git
```bash
sudo apt install -y git build-essential
```

### 3. Install 3proxy from Source
```bash
sudo git clone https://github.com/z3APA3A/3proxy.git
cd 3proxy
sudo make -f Makefile.Linux
sudo make -f Makefile.Linux install
```
Verify the installation:
```bash
which 3proxy
```

### 4. Firewall Setup (UFW)
If you are running on a server, you must open the necessary ports:
```bash
sudo apt install ufw
sudo ufw allow ssh
sudo ufw allow 8000:8020/tcp   # Proxy ports range
sudo ufw enable
```

---

## Configuration

### VPN Credentials
You need a Proton VPN account. The free version is perfectly fine to start with, providing access to more than 10 countries and over 100 IPs.
The paid version (€9.99/mo) offers 125+ countries and 17,800+ IPs.

1. Download your `.ovpn` config files from Proton VPN and place them in the `vpn_configs/` directory, organized by country (e.g., `vpn_configs/canada/`).
   ![Proton VPN Configs](assets/proton_vpn_configs.png)
2. Create a `.env` file in the project root:
```bash
cp .env_example .env
```
3. Edit `.env` and add your Proton VPN OpenVPN credentials (found in your Proton VPN account dashboard, NOT your regular login password):
   ![Proton VPN Credentials](assets/proton_vpn_creds.png)
```env
OPENVPN_USER=your_openvpn_username
OPENVPN_PASS=your_openvpn_password

PROXY_USER=your_desired_proxy_username
PROXY_PASS=your_desired_proxy_password

# REST API settings (optional)
API_HOST=0.0.0.0
API_PORT=8080
API_AUTH_ENABLED=0
API_USER=your_api_username
API_PASS=your_api_password
```

---

## How to Run

You can run the project using Python directly, `uv`, or `make`.

### Using Makefile (Recommended)
```bash
# Install Python dependencies
make install

# View available countries
make list-countries

# View available configs for a specific country
make list-configs country=usa

# Check status of running proxies
make status

# Stop all proxies
make stop-all

# Start the REST API server
make api
```

### Using Python or uv
```bash
# List all countries
sudo uv run proxy-list-countries

# List configs for a specific country
sudo uv run proxy-list-configs usa

# Start a proxy
# Usage: sudo uv run proxy-start <country> <config_name> <port> [--label <label>]
sudo uv run proxy-start usa us-free-44 8011 --label "user-1"

# Stop a proxy
sudo uv run proxy-stop 8011

# View logs
sudo uv run proxy-logs 8011

# Start REST API server
sudo uv run proxy-api
```

---

## REST API

ProxyForFree includes a built-in REST API (powered by FastAPI) for managing proxies programmatically.

### Starting the API Server
```bash
# Default: listens on 0.0.0.0:8080
make api

# Or with custom host/port via environment variables
API_HOST=127.0.0.1 API_PORT=9000 sudo uv run proxy-api
```

Once running, interactive docs are available at `http://<host>:<port>/docs` (Swagger UI) and `http://<host>:<port>/redoc` (ReDoc).

### Authentication (optional)
Set `API_AUTH_ENABLED=1` in your `.env` file to protect the API with HTTP Basic Auth using `API_USER` / `API_PASS` credentials.

### API Endpoints

| Method | Endpoint                      | Description                            |
|--------|-------------------------------|----------------------------------------|
| GET    | `/`                           | Health check                           |
| GET    | `/health`                     | Health check                           |
| GET    | `/api/v1/countries`           | List available VPN countries           |
| GET    | `/api/v1/configs?country=usa` | List VPN configs (optionally by country) |
| GET    | `/api/v1/proxies/status`      | Get status of all running proxies      |
| GET    | `/api/v1/proxies/logs/{port}` | Get OpenVPN logs for a proxy           |
| POST   | `/api/v1/proxies/start`       | Start a new proxy                      |
| POST   | `/api/v1/proxies/stop`        | Stop a proxy                           |
| POST   | `/api/v1/proxies/stop-all`    | Stop all proxies                       |

### Example Usage

**List countries:**
```bash
curl http://localhost:8080/api/v1/countries
```

**Start a proxy:**
```bash
curl -X POST http://localhost:8080/api/v1/proxies/start \
  -H "Content-Type: application/json" \
  -d '{"country": "usa", "config": "us-free-44", "port": 8011, "label": "user-123"}'
```

**Check status:**
```bash
curl http://localhost:8080/api/v1/proxies/status
```

**Stop a proxy:**
```bash
curl -X POST http://localhost:8080/api/v1/proxies/stop \
  -H "Content-Type: application/json" \
  -d '{"port": 8011}'
```

**Stop all proxies:**
```bash
curl -X POST http://localhost:8080/api/v1/proxies/stop-all
```

---

## How it Works
The script uses **Policy Routing** (`ip rule`). Each OpenVPN connection gets its own `tun` interface and a dedicated routing table. 3proxy binds to the specific IP of the `tun` interface, forcing all outgoing traffic through that VPN. This allows you to run dozens of proxies simultaneously on a single machine, each with a different exit IP.

---

### ⚠️ Disclaimer

This repository is created solely for **educational and research purposes**. Use the knowledge acquired responsibly and respect the terms of use of websites. The authors are not responsible for any misuse of the materials.

---

### ⭐ Star History

If this project was useful to you, give it a star! ⭐

---
