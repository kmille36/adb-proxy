import asyncio
import uri
import string
import random

async def check_call(program, *args, **kwargs):
    proc = await asyncio.create_subprocess_exec(program, *args, **kwargs)
    exitcode = await proc.wait()
    if exitcode != 0:
        raise Exception(f"{program} exited with code {exitcode}")


def sockaddr(addr):
    parsed = uri.URI('//' + addr + "/")
    return parsed.hostname, parsed.port


def ssh_config(config):
    parsed = uri.URI('//' + config + "/")
    ret = {
        "known_hosts": None,
    }
    if parsed.username is not None:
        ret["username"] = parsed.username
    if parsed.password is not None:
        ret["password"] = parsed.password
    if parsed.hostname is not None:
        ret["host"] = parsed.hostname
    if parsed.port is not None:
        ret["port"] = parsed.port
    return ret

def hostport(sockaddr):
    return ssh_uri({"host": sockaddr[0], "port": sockaddr[1]})

def ssh_uri(sockaddr):
    return uri.URI(
        username=sockaddr.get("username"),
        password="***" if sockaddr.get("password") is not None else None,
        hostname=sockaddr.get("host"),
        port=sockaddr.get("port")
    ).uri[2:-1]

def random_str(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
