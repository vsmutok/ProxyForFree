#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

from cli.commands import (
    cmd_list_configs,
    cmd_list_countries,
    cmd_logs,
    cmd_start,
    cmd_status,
    cmd_stop,
    cmd_stop_all,
)
from core.config import OPENVPN_PASS, OPENVPN_USER


def check_dependencies():
    """Verify that required system tools are installed."""
    for cmd in ["openvpn", "3proxy", "ip"]:
        if subprocess.run(["which", cmd], stdout=subprocess.DEVNULL).returncode != 0:
            print(f"Error: {cmd} is not installed.")
            sys.exit(1)


def check_auth():
    """Check if OpenVPN credentials are provided in environment variables."""
    if not OPENVPN_USER or not OPENVPN_PASS:
        print("Error: OPENVPN_USER and OPENVPN_PASS environment variables must be set.")
        print("Example: export OPENVPN_USER=your_user OPENVPN_PASS=your_pass")
        sys.exit(1)


def main():
    """Main entry point for the Proxy Manager CLI."""
    if os.getuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

    check_dependencies()
    check_auth()

    parser = argparse.ArgumentParser(description="Proxy Manager (OpenVPN + 3proxy)")
    subparsers = parser.add_subparsers(dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a new proxy")
    start_parser.add_argument("country", help="Country folder name")
    start_parser.add_argument("config", help="Config file name (with or without .ovpn)")
    start_parser.add_argument("port", type=int, help="Port for the proxy")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a proxy")
    stop_parser.add_argument("port", type=int, help="Port of the proxy to stop")

    # Stop-all command
    subparsers.add_parser("stop-all", help="Stop all proxies and cleanup")

    # List configs command
    list_cfg_parser = subparsers.add_parser("list-configs", help="List available VPN configurations")
    list_cfg_parser.add_argument("country", nargs="?", help="Country to list configs for")

    # List countries command
    subparsers.add_parser("list-countries", help="List available countries")

    # Status command
    subparsers.add_parser("status", help="Show running proxies")

    # Logs command
    log_parser = subparsers.add_parser("logs", help="Show OpenVPN logs for a port")
    log_parser.add_argument("port", type=int, help="Port of the proxy")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args.country, args.config, args.port)
    elif args.command == "stop":
        cmd_stop(args.port)
    elif args.command == "stop-all":
        cmd_stop_all()
    elif args.command == "list-configs":
        cmd_list_configs(args.country)
    elif args.command == "list-countries":
        cmd_list_countries()
    elif args.command == "status":
        cmd_status()
    elif args.command == "logs":
        cmd_logs(args.port)
    else:
        parser.print_help()


def main_start():
    sys.argv.insert(1, "start")
    main()


def main_stop():
    sys.argv.insert(1, "stop")
    main()


def main_stop_all():
    sys.argv.insert(1, "stop-all")
    main()


def main_status():
    sys.argv.insert(1, "status")
    main()


def main_logs():
    sys.argv.insert(1, "logs")
    main()


def main_list_configs():
    sys.argv.insert(1, "list-configs")
    main()


def main_list_countries():
    sys.argv.insert(1, "list-countries")
    main()


if __name__ == "__main__":
    main()
