def bytes2bools(bytes):
    ret = []
    for b in reversed(bytes):
        single_byte = [False] * 8
        for i in range(8):
            single_byte[i] = (b & 1 == 1)
            b >>= 1
            if b == 0:
                break
        ret += single_byte
    return ret

