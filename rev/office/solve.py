from hashlib import md5
import itertools

CHUNKS = [
    [4072117587, 1120387196, 2102578019, 85756587],
    [3002749583, 3716679707, 3074522701, 1912839214],
    [1202946202, 3060285146, 3794539838, 3225098655],
    [4005615615, 2391617212, 2576942536, 2140002521],
    [1783887626, 3622230939, 1267188250, 2483512918],
    [3971983597, 866610566, 1921144098, 402180923],
    [3409560921, 3103012121, 2261944769, 3919384297],
    [3377601125, 847392938, 543800179, 879909070],
    [2343965920, 2169933120, 1366115365, 931825985],
    [1416552657, 3925964814, 413409308, 1810266362],
]

flag = [ord("?")] * 30


for chunk_i, chunk in enumerate(CHUNKS):
    for guess in itertools.product(range(256), repeat=3):
        digest = md5(b"s0me_sn34ky_s4lt" + bytes(guess)).digest()
        a0, b0, c0, d0 = digest[:4], digest[4:8], digest[8:12], digest[12:16]
        a0, b0, c0, d0 = [int.from_bytes(b, byteorder="little") for b in [a0, b0, c0, d0]]

        if a0 == chunk[0] and b0 == chunk[1] and c0 == chunk[2] and d0 == chunk[3]:
            print(guess, bytes(guess))
            for i in range(3):
                flag[i * 10 + chunk_i] = guess[i]
            print(bytes(flag))
            break
