from .RandomPermute import RandomPermuter


class ArbitaryWidthRandomPermute(object):
    '''
    This module is NOT reliable for encrypt.

    Carefully used.
    Usage:
        >>> awrp = ArbitaryWidthRandomPermute(12306, 10)
        >>> awrp.permute(2015)
    '''

    _grouped_by = 4

    def __init__(self, key, width, keeped=None):
        self.keeped = keeped if keeped is not None else (lambda x: False)
        self.width = width
        self.key = key
        self.random_permuters = dict()

    def _in_range(self, output):
        return 10 ** (self.width - 1) <= output < 10 ** self.width

    def _get_permuter(self, key, width):
        if (key, width) not in random_permuters:
            random_permuters[(key, width)] = RandomPermuter(output, grp)
        return random_permuters[(key, width)]

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
    from datetime import datetime

    # test speed
    for N in range(2, 30):
        start_t = datetime.now()
        awrp = ArbitaryWidthRandomPermute(1008611, N)
        for i in range(100):
            awrp.permute(i)
        end_t = datetime.now()
        print('%d bit permuted (100 times) takes %s' % (N, end_t - start_t))

    # test validity
    test_bits = 5
    awrp = ArbitaryWidthRandomPermute(1008611, test_bits)
    found = set()
    for i in range(10 ** test_bits):
        res = awrp.permute(i)
        print('%d -->' % i, res)
        if res is None:
            continue
        if res in found:
            raise Exception('Output is not unique')
        if not 10 ** (test_bits-1) <= res < 10 ** test_bits:
            raise Exception('Output is not in given range')
        found.add(res)
    print('%d unique number generated.' % len(found))
