def convert_duration(values_ns, fmt):
    if fmt == "ns":
        return values_ns
    if fmt == "ms":
        return values_ns / 1e6
    if fmt == "s":
        return values_ns / 1e9
    raise ValueError("Invalid duration format")


def bytes_to_mb(values):
    return values / (1024**2)
