def chech(piece, target):
    raw = piece.encode()
    x = int.from_bytes(raw, "big")
    return (1337 * x + 424242) % (256 ** len(raw)) == target
