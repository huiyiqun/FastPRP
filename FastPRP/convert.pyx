from .exception import InputNotInRange

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


def uint2bytes(uint, length):
    ret = [0] * length
    for i in range(length):
        ret[i] = uint & 255
        uint >>= 8
        if uint == 0:
            break
    else:
        print(uint, length)
        raise InputNotInRange()
    return bytes(reversed(ret))


def uint2bools(uint, length):
    ret = [False] * length
    for i in range(length):
        ret[i] = (uint & 1 == 1)
        uint >>= 1
        if uint == 0:
            return ret
    raise InputNotInRange()

