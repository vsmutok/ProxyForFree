import contextlib
import os
import re
import signal
import subprocess
from pathlib import Path

from core.config import CONFIG_DIR, OPENVPN_PASS, OPENVPN_USER


class VPNManager:
    """
    Handles OpenVPN process management and routing configuration.
    """

    def __init__(self, config_dir=CONFIG_DIR):
        self.config_dir = config_dir

    def get_tun_ip(self, interface):
        """
        Get the IP address assigned to a specific TUN interface.

        Args:
            interface (str): The name of the TUN interface.

        Returns:
            str or None: The IP address if found.
        """
        try:
            output = subprocess.check_output(["ip", "addr", "show", interface], stderr=subprocess.STDOUT).decode()
            match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", output)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None

    def list_countries(self):
        """
        Return a list of available countries.
        """
        config_dir = Path(self.config_dir)
        if not config_dir.exists():
            return []
        return sorted([d.name for d in config_dir.iterdir() if d.is_dir()])

    def list_configs(self, country=None):
        """
        Get available VPN configurations.
        """
        config_dir = Path(self.config_dir)
        if not config_dir.exists():
            return {}

        result = {}
        if country:
            country_path = config_dir / country
            if country_path.exists():
                result[country] = sorted([f.name for f in country_path.iterdir() if f.name.endswith(".ovpn")])
        else:
            countries = self.list_countries()
            for c in countries:
                configs = sorted([f.name for f in (config_dir / c).iterdir() if f.name.endswith(".ovpn")])
                result[c] = configs
        return result

    def setup_vpn_process(self, country, config_name, port, tun_interface):
        """
        Start the OpenVPN process.
        """
        config_path = Path(self.config_dir) / country / config_name
        if not config_name.endswith(".ovpn") and not config_path.exists():
            config_path = Path(f"{config_path}.ovpn")

        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        ovpn_pid_file = f"/tmp/ovpn_{port}.pid"
        ovpn_log_file = f"/tmp/ovpn_{port}.log"
        ovpn_auth_file = f"/tmp/ovpn_auth_{port}.tmp"
        temp_ovpn_cfg = f"/tmp/ovpn_cfg_{port}.ovpn"

        # Cleanup old files
        for f_path in [ovpn_log_file, ovpn_auth_file]:
            f = Path(f_path)
            if f.exists():
                with contextlib.suppress(Exception):
                    f.unlink()

        # Create temporary auth file from ENV
        try:
            auth_file = Path(ovpn_auth_file)
            with auth_file.open("w") as f:
                f.write(f"{OPENVPN_USER or ''}\n{OPENVPN_PASS or ''}\n")
            auth_file.chmod(0o600)
        except Exception as e:
            raise RuntimeError(f"Failed to create temp auth file: {e}") from e

        # Prepare temp config
        try:
            temp_cfg = Path(temp_ovpn_cfg)
            with config_path.open() as f_in, temp_cfg.open("w") as f_out:
                for line in f_in:
                    if re.match(r"^\s*(up|down|script-security)\s+", line):
                        f_out.write(f"# {line}")
                    else:
                        f_out.write(line)
            config_to_use = str(temp_cfg)
        except Exception:
            config_to_use = str(config_path)

        ovpn_cmd = [
            "openvpn",
            "--config",
            config_to_use,
            "--auth-user-pass",
            ovpn_auth_file,
            "--dev",
            tun_interface,
            "--route-nopull",
            "--daemon",
            "--writepid",
            ovpn_pid_file,
            "--log",
            ovpn_log_file,
        ]

        # Check OpenVPN version for DCO support
        try:
            version_out = subprocess.check_output(["openvpn", "--version"], text=True).splitlines()[0]
            if " 2.6." in version_out:
                ovpn_cmd.append("--disable-dco")
        except Exception:
            pass

        result = subprocess.run(ovpn_cmd, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
            with Path(ovpn_log_file).open("a") as f:
                f.write(f"\nStartup Error: {result.stderr}\n")

        return result.returncode, ovpn_log_file, temp_ovpn_cfg

    def setup_routing(self, port, tun_ip, tun_interface):
        """
        Setup IP rules and routing table for the proxy.
        """
        port_str = str(port)
        subprocess.run(["ip", "rule", "add", "from", tun_ip, "table", port_str])
        subprocess.run(["ip", "route", "add", "default", "dev", tun_interface, "table", port_str])

    def cleanup_routing(self, port, tun_ip=None):
        """
        Clean up IP rules and routing tables.
        """
        port_str = str(port)
        if tun_ip:
            subprocess.run(["ip", "rule", "del", "from", tun_ip, "table", port_str], stderr=subprocess.DEVNULL)

        subprocess.run(["ip", "route", "flush", "table", port_str], stderr=subprocess.DEVNULL)

        try:
            rules = subprocess.check_output(["ip", "rule", "show"]).decode()
            for line in rules.splitlines():
                if f"lookup {port_str}" in line or f"table {port_str}" in line:
                    rule_match = re.match(r"(\d+):\s+(.*)\s+(lookup|table)", line)
                    if rule_match:
                        rule_spec = rule_match.group(2).strip()
                        subprocess.run(["ip", "rule", "del"] + rule_spec.split(), stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def stop_vpn_processes(self, port):
        """
        Stop OpenVPN and 3proxy processes for a specific port.
        """
        for pid_file_path in [f"/tmp/ovpn_{port}.pid", f"/tmp/3proxy_{port}.pid"]:
            pid_file = Path(pid_file_path)
            if pid_file.exists():
                # Kills process; removes PID file on failure
                try:
                    with pid_file.open() as f:
                        pid = int(f.read().strip())
                        os.kill(pid, signal.SIGTERM)
                    pid_file.unlink()
                except Exception:
                    if pid_file.exists():
                        pid_file.unlink()

        # Also cleanup temp auth file
        auth_file = Path(f"/tmp/ovpn_auth_{port}.tmp")
        if auth_file.exists():
            with contextlib.suppress(Exception):
                auth_file.unlink()
