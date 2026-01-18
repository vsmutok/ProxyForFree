import subprocess
import time
from pathlib import Path

from core.state import StateManager
from proxy.instance import ProxyInstance
from proxy.server import ProxyServer
from vpn.manager import VPNManager


class ProxyApp:
    """
    Main application class for Proxy Manager CLI.
    """

    def __init__(self):
        self.state_manager = StateManager()
        self.vpn_manager = VPNManager()
        self.proxy_server = ProxyServer()

    def start_proxy(self, country, config, port):
        """Start a new proxy instance."""
        port_str = str(port)
        state = self.state_manager.get_state()

        instance = ProxyInstance(port, self.vpn_manager, self.proxy_server)

        if port_str in state:
            print(f"Port {port} is already recorded in state.")
            # Verify if it's actually running
            running, pid = instance.is_running()
            if running:
                print(f"Error: Process with PID {pid} is already running for port {port}.")
                return
            print("It seems to be an orphaned state. Cleaning up...")
            del state[port_str]
            self.state_manager.save_state(state)

        running, pid = instance.is_running()
        if running:
            print(f"Error: Process with PID {pid} is already running for port {port}. Please run 'stop {port}' first.")
            return

        print(f"Starting OpenVPN for {country}/{config} on {instance.tun_interface}...")
        success, result = instance.start(country, config)

        if not success:
            print(f"Error: {result}")
            # Give it a moment to flush logs to disk
            time.sleep(2)
            if Path(instance.ovpn_log_file).exists():
                print("\nLast 20 lines of OpenVPN log:")
                subprocess.run(["tail", "-n", "20", instance.ovpn_log_file])
            return

        tun_ip = result
        print(f"Interface {instance.tun_interface} got IP: {tun_ip}")

        state[port_str] = {
            "country": country,
            "config": config,
            "tun_interface": instance.tun_interface,
            "tun_ip": tun_ip,
            "start_time": time.ctime(),
        }
        self.state_manager.save_state(state)
        print(f"Proxy successfully started on port {port}")

    def stop_proxy(self, port):
        """Stop a specific proxy instance."""
        state = self.state_manager.get_state()
        port_str = str(port)
        info = state.get(port_str, {})

        print(f"Stopping proxy on port {port}...")

        instance = ProxyInstance(port, self.vpn_manager, self.proxy_server)
        instance.stop(info.get("tun_ip"))

        if port_str in state:
            del state[port_str]
            self.state_manager.save_state(state)
        print(f"Proxy on port {port} stopped and cleaned up.")

    def stop_all_proxies(self):
        """Stop all running proxies."""
        state = self.state_manager.get_state()
        ports = set(state.keys())

        # Also find any pid files in /tmp that might not be in state
        for pid_file in Path("/tmp").glob("ovpn_*.pid"):
            try:
                port = pid_file.name.split("_")[-1].split(".")[0]
                ports.add(port)
            except Exception:
                pass

        if not ports:
            print("No active proxies or PID files found.")
            return

        for port in sorted(ports, key=int):
            self.stop_proxy(port)

    def list_countries(self):
        """List all available countries."""
        countries = self.vpn_manager.list_countries()
        if not countries:
            print("No countries found in vpn_configs.")
            return
        for country in countries:
            print(country)

    def list_configs(self, country=None):
        """List available VPN configurations."""
        configs = self.vpn_manager.list_configs(country)
        if not configs:
            print("No configurations found.")
            return

        if country:
            if country in configs:
                for cfg in configs[country]:
                    print(cfg)
            else:
                print(f"Country {country} not found.")
        else:
            for c, cfg_list in configs.items():
                print(f"Country: {c}")
                for cfg in cfg_list:
                    print(f"  - {cfg}")

    def show_status(self):
        """Show the status of running proxies."""
        state = self.state_manager.get_state()
        if not state:
            print("No proxies running.")
            return

        print(f"{'PORT':<8} {'COUNTRY':<15} {'CONFIG':<30} {'TUN IP':<15} {'STARTED'}")
        print("-" * 80)
        for port, info in state.items():
            print(f"{port:<8} {info['country']:<15} {info['config']:<30} {info['tun_ip']:<15} {info['start_time']}")

    def show_logs(self, port):
        """Show OpenVPN logs for a specific port."""
        log_file = Path(f"/tmp/ovpn_{port}.log")
        if log_file.exists():
            print(f"--- OpenVPN logs for port {port} ---")
            subprocess.run(["cat", str(log_file)])
        else:
            print(f"No log file found for port {port}. Use 'status' to see running proxies.")


# Keep legacy functional wrappers for compatibility if needed,
# or just export the class. Since proxy_manager.py uses individual functions,
# let's update them to use ProxyApp.

_app = ProxyApp()


def cmd_start(country, config, port):
    _app.start_proxy(country, config, port)


def cmd_stop(port):
    _app.stop_proxy(port)


def cmd_stop_all():
    _app.stop_all_proxies()


def cmd_list_countries():
    _app.list_countries()


def cmd_list_configs(country=None):
    _app.list_configs(country)


def cmd_status():
    _app.show_status()


def cmd_logs(port):
    _app.show_logs(port)
