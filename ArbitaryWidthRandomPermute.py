from RandomPermute import RandomPermuter


class ArbitaryWidthRandomPermute(object):
    '''
    This module is NOT reliable for encrypt.

    Carefully used.
    Usage:
        >>> awrp = ArbitaryWidthRandomPermute(12306, 10)
        >>> awrp.permute(2015)
    '''

    _grouped_by = 5

    def __init__(self, key, width, keeped=None):
        self.keeped = keeped if keeped is not None else (lambda x: False)
        self.width = width
        self.key = key

    def _in_range(self, output):
        return 10 ** (self.width - 1) <= output < 10 ** self.width

    def permute(self, input):
        ret = 0
        grp = 10 ** self._grouped_by
        output = self.key  # self.key as initial output(first key)
        width = self.width
        while width > self._grouped_by:
            rp = RandomPermuter(output, grp)
            ret *= grp
            output = rp.permute(input % grp)
            ret += output
            input //= grp
            width -= self._grouped_by
        rp = RandomPermuter(output, 10 ** width)
        ret *= 10 ** width
        ret += rp.permute(input)

        if self.keeped(ret) or not self._in_range(ret):
            return None
        return ret

if __name__ == '__main__':
    awrp = ArbitaryWidthRandomPermute(1008611, 10)
    for i in range(100):
        print('%d -->' % i, awrp.permute(i))
