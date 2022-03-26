import platform

def is_unix() -> bool:
    sysname = platform.system()

    if not sysname:
        # if the system type cannot not be determined, assume a Unix based system
        return True

    return sysname == "Darwin" or sysname == "Linux"