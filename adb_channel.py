from util import *

def device_path(device_id):
    return f"host:transport:{device_id}"


async def open_stream(adb_connect, *path):
    """ Open a stream to the device """
    reader, writer = await adb_connect()

    try:
        for cmd in path:
            cmd = cmd.encode("utf-8")
            data = "{0:04X}".format(len(cmd)).encode("utf-8") + cmd
            writer.write(data)
            await writer.drain()

            status = (await reader.readexactly(4))
            if status != b'OKAY':
                if status == b'FAIL':
                    size = int(await reader.readexactly(4), 16)
                    message = (await reader.readexactly(size)).decode('utf-8')
                    raise Exception(f"Cannot open '{cmd}': {status}: {message}")
                else:
                    raise Exception(f"Cannot open '{cmd}': Unknown status {status}")

        return reader, writer

    except:
        await close_and_wait(writer)
        raise


async def read_stream(*args, **kwargs):
    """ Open a stream to the device, read its contents and close """
    reader, writer = await open_stream(*args, **kwargs)
    try:
        return await reader.read()
    finally:
        await close_and_wait(writer)

async def list_adb_devices(adb_connect):
    lines = (await read_stream(adb_connect, "host:devices"))[4:].decode('utf-8').splitlines()
    ret = []
    for line in lines:
        line = line.strip()
        name, type = line.split("\t")
        if type == "device":
            ret.append(name)
    return ret
