def list_chunk(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]
