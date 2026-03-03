import time
from pathlib import Path

from core.state import StateManager
from proxy.instance import ProxyInstance
from proxy.server import ProxyServer
from vpn.manager import VPNManager


class ProxyService:
    """
    Core business logic for proxy management.
    Returns data instead of printing — suitable for both CLI and API.
    """

    def __init__(self):
        self.state_manager = StateManager()
        self.vpn_manager = VPNManager()
        self.proxy_server = ProxyServer()

    def start_proxy(self, country: str, config: str, port: int) -> dict:
        """Start a new proxy instance. Returns dict with 'success' and 'message'."""
        port_str = str(port)
        state = self.state_manager.get_state()
        instance = ProxyInstance(port, self.vpn_manager, self.proxy_server)

        if port_str in state:
            running, pid = instance.is_running()
            if running:
                return {"success": False, "message": f"Process with PID {pid} is already running for port {port}."}
            # Orphaned state — clean up
            del state[port_str]
            self.state_manager.save_state(state)

        running, pid = instance.is_running()
        if running:
            return {
                "success": False,
                "message": f"Process with PID {pid} is already running for port {port}. Stop it first.",
            }

        success, result = instance.start(country, config)

        if not success:
            log_tail = ""
            time.sleep(2)
            log_path = Path(instance.ovpn_log_file)
            if log_path.exists():
                log_tail = log_path.read_text()[-2000:]
            return {"success": False, "message": f"Failed to start: {result}", "log_tail": log_tail}

        tun_ip = result
        state[port_str] = {
            "country": country,
            "config": config,
            "tun_interface": instance.tun_interface,
            "tun_ip": tun_ip,
            "start_time": time.ctime(),
        }
        self.state_manager.save_state(state)
        return {"success": True, "message": f"Proxy started on port {port}", "tun_ip": tun_ip}

    def stop_proxy(self, port: int) -> dict:
        """Stop a specific proxy instance."""
        state = self.state_manager.get_state()
        port_str = str(port)
        info = state.get(port_str, {})

        instance = ProxyInstance(port, self.vpn_manager, self.proxy_server)
        instance.stop(info.get("tun_ip"))

        if port_str in state:
            del state[port_str]
            self.state_manager.save_state(state)

        return {"success": True, "message": f"Proxy on port {port} stopped and cleaned up."}

    def stop_all_proxies(self) -> dict:
        """Stop all running proxies."""
        state = self.state_manager.get_state()
        ports = set(state.keys())

        for pid_file in Path("/tmp").glob("ovpn_*.pid"):
            try:
                port = pid_file.name.split("_")[-1].split(".")[0]
                ports.add(port)
            except Exception:
                pass

        if not ports:
            return {"success": True, "message": "No active proxies found.", "stopped": []}

        stopped = []
        for port in sorted(ports, key=int):
            self.stop_proxy(int(port))
            stopped.append(port)

        return {"success": True, "message": f"Stopped {len(stopped)} proxies.", "stopped": stopped}

    def list_countries(self) -> list[str]:
        """List available countries."""
        return self.vpn_manager.list_countries()

    def list_configs(self, country: str | None = None) -> dict[str, list[str]]:
        """List available VPN configurations."""
        return self.vpn_manager.list_configs(country)

    def get_status(self) -> dict:
        """Get status of all running proxies."""
        state = self.state_manager.get_state()
        proxies = []
        for port, info in state.items():
            proxies.append(
                {
                    "port": port,
                    "country": info.get("country", ""),
                    "config": info.get("config", ""),
                    "tun_interface": info.get("tun_interface", ""),
                    "tun_ip": info.get("tun_ip", ""),
                    "start_time": info.get("start_time", ""),
                }
            )
        return {"proxies": proxies, "total": len(proxies)}

    def get_logs(self, port: int) -> dict:
        """Get OpenVPN logs for a specific port."""
        log_file = Path(f"/tmp/ovpn_{port}.log")
        if log_file.exists():
            return {"success": True, "port": port, "logs": log_file.read_text()}
        return {"success": False, "port": port, "message": f"No log file found for port {port}."}
