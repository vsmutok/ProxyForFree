import contextlib
import os
import time
from pathlib import Path

from proxy.server import ProxyServer
from vpn.manager import VPNManager


class ProxyInstance:
    """
    Represents a single proxy instance (OpenVPN + 3proxy).
    """

    def __init__(self, port, vpn_manager: VPNManager, proxy_server: ProxyServer):
        self.port = port
        self.vpn_manager = vpn_manager
        self.proxy_server = proxy_server
        self.tun_interface = f"tun{port}"
        self.port_str = str(port)
        self.ovpn_pid_file = f"/tmp/ovpn_{port}.pid"
        self.ovpn_log_file = f"/tmp/ovpn_{port}.log"
        self.temp_ovpn_cfg = f"/tmp/ovpn_cfg_{port}.ovpn"
        self.proxy_cfg_file = f"/tmp/3proxy_{port}.cfg"

    def is_running(self):
        """Check if any processes are running for this port."""
        for pid_file_path in [self.ovpn_pid_file, f"/tmp/3proxy_{self.port}.pid"]:
            pid_file = Path(pid_file_path)
            if pid_file.exists():
                try:
                    with pid_file.open() as f:
                        pid = int(f.read().strip())
                    os.kill(pid, 0)
                    return True, pid
                except Exception:
                    if pid_file.exists():
                        pid_file.unlink()
        return False, None

    def start(self, country, config):
        """Starts the OpenVPN and 3proxy for this instance."""
        ret_code, log_file, temp_cfg = self.vpn_manager.setup_vpn_process(
            country, config, self.port, self.tun_interface
        )

        if ret_code != 0:
            return False, "Failed to start OpenVPN process"

        # Give it a moment to initialize and create PID file
        time.sleep(2)

        # Wait for IP
        tun_ip = None
        for _ in range(30):
            running, _ = self.is_running()
            if not running:
                return False, "OpenVPN process died unexpectedly"

            tun_ip = self.vpn_manager.get_tun_ip(self.tun_interface)
            if tun_ip:
                break
            time.sleep(1)

        if not tun_ip:
            error_msg = "Failed to get IP for interface (timeout)"
            self.stop()  # Cleanup
            return False, error_msg

        # Setup routing
        self.vpn_manager.setup_routing(self.port, tun_ip, self.tun_interface)

        # Start 3proxy
        self.proxy_server.start_3proxy(self.port, tun_ip)

        return True, tun_ip

    def stop(self, tun_ip=None):
        """Stops all processes and cleans up resources."""
        self.vpn_manager.stop_vpn_processes(self.port)

        ovpn_log = Path(self.ovpn_log_file)
        if ovpn_log.exists():
            with contextlib.suppress(Exception):
                ovpn_log.unlink()

        self.vpn_manager.cleanup_routing(self.port, tun_ip)

        for f_path in [self.temp_ovpn_cfg, self.proxy_cfg_file]:
            f = Path(f_path)
            if f.exists():
                with contextlib.suppress(Exception):
                    f.unlink()
