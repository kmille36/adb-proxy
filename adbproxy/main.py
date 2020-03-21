from .adb_proxy import *
from .util import *

async def main():
    parser = argparse.ArgumentParser(description="Creates ADB Proxy connections")

    ssh_jump_parser = argparse.ArgumentParser(add_help=False)
    ssh_jump_parser.add_argument("-J", "--ssh-tunnel", dest="ssh_tunnels", action="append", type=ssh_config, help="Add a SSH jump host to access the remote address")

    deviceinfo_parser = argparse.ArgumentParser(add_help=False)
    deviceinfo_parser.add_argument("-s", "--serial", dest="device_id", help="Device serial number")
    deviceinfo_parser.add_argument("--device-adb-server", dest="device_adb_addr", type=sockaddr, default=("localhost", 5037), help="Socket address of ADB server attached to the device")
    deviceinfo_parser.add_argument("--no-adb-reverse", dest="adb_reverse_supported", action="store_false", help="Disables reverse connection proxy (device->host)")
    deviceinfo_parser.add_argument("--share", dest="share", action="store_true", help="Swaps the roles of local and remote endpoints (Shares a local device with a remote computer)")

    hostinfo_parser = argparse.ArgumentParser(add_help=False)
    hostinfo_parser.add_argument("--host-adb-server", dest="host_adb_addr", type=sockaddr, default=("localhost", 5037), help="Socket address of ADB server away from the device")

    listen_reverser_base_parser = argparse.ArgumentParser(add_help=False, parents=[hostinfo_parser, ssh_jump_parser])
    listen_reverser_base_parser.add_argument("listen_address", type=ssh_config, nargs='?', default={}, help="Server address where the reverse SSH server will be bound")
    listen_reverser_base_parser.add_argument("--upnp", action='store_true', help="Uses UPNP to setup the Internet Gateway to receive incoming connections")

    subparsers = parser.add_subparsers(help='commands', dest='cmd')
    subparsers.required = True

    parser_connect_client = subparsers.add_parser('connect', parents=[deviceinfo_parser, hostinfo_parser, ssh_jump_parser], help='Makes a direct connection to the device ADB')
    parser_connect_client.set_defaults(func=connect)

    parser_connect_reverse = subparsers.add_parser('connect-reverse', parents=[deviceinfo_parser, ssh_jump_parser], help='Creates a reverse connection to a remote server created with listen-reverse')
    parser_connect_reverse.add_argument("server_address", type=ssh_config, nargs='?', default={}, help="Address that the remote ADB-Proxy is listening on")
    parser_connect_reverse.set_defaults(func=connect_reverse)

    parser_listen_reverse = subparsers.add_parser('listen-reverse', parents=[listen_reverser_base_parser], help='Awaits reverse connections from devices')
    parser_listen_reverse.set_defaults(func=listen_reverse)

    parser_df = subparsers.add_parser('device-farm', parents=[listen_reverser_base_parser], help='Awaits connections from DeviceFarm')
    parser_df.add_argument("--project", dest='project_name', default="Remote Debug", help="Project Name")
    parser_df.add_argument("--device-pool", dest='device_pool', default="Default Pool", help="Device Pool")
    parser_df.set_defaults(func=devicefarm)

    argcomplete.autocomplete(parser)
    args = parser.parse_args().__dict__
    del args["cmd"]

    await use_tunnels(**args)


def main_sync():
    return asyncio_run(main(), debug=True)
