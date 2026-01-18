import subprocess
from pathlib import Path

from core.config import PROXY_PASS, PROXY_USER


class ProxyServer:
    """
    Manages the 3proxy server configuration and process.
    """

    def __init__(self, user=PROXY_USER, password=PROXY_PASS):
        self.user = user
        self.password = password

    def start_3proxy(self, port, tun_ip):
        """
        Generate configuration and start the 3proxy server.

        Args:
            port (int): The port to listen on.
            tun_ip (str): The external IP address to use for outgoing connections.
        """
        proxy_cfg_file = f"/tmp/3proxy_{port}.cfg"
        proxy_pid_file = f"/tmp/3proxy_{port}.pid"

        proxy_cfg = Path(proxy_cfg_file)
        with proxy_cfg.open("w") as f:
            f.write("daemon\n")
            f.write(f"pidfile {proxy_pid_file}\n")
            f.write("nserver 8.8.8.8\n")
            f.write("nserver 8.8.4.4\n")
            f.write(f"users {self.user}:CL:{self.password}\n")
            f.write("auth strong\n")
            f.write(f"allow {self.user}\n")
            f.write(f"proxy -p{port} -e{tun_ip}\n")

        subprocess.run(["3proxy", proxy_cfg_file])
