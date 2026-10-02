import base64


def cheque(piece, target):
    return base64.b85encode(base64.b32encode(base64.b64encode(piece.encode()))) == target
