import time

def timestamp() -> int:
    return int(time.time())


def yesterday_midnight() -> int:
    return (int(time.time() // 86400)) * 86400 - 86400
