def list_chunk(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def to_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default
