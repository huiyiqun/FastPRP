from bitstring import BitArray
from Crypto.Cipher import DES
from datetime import datetime


class InputNotInRange(Exception):
    pass


class NotImplemented(Exception):
    pass


#class BitArray(object):
    #'''
    #For BitArray from bitstring is not efficient,
    #I try to re-implement a version with same interface
    #but less functions.
    #'''
    #pass


class RandomBits(object):
    '''
    Random bytess with unlimited length, It's lazily loaded
    (generated when queried) and cached(multiple query for same bytes
    will be cached)

    Example:
        >>> rb = RandomBits(543252234)
        >>> rb[512] == 1
    '''
    KEY_LENGTH = 64  # DES needs 8 bytes-length key

    # DES encrypts 8 bytes-length string into 8 bytes-length
    # string per operation
    STRING_LENGTH = 64

    def __init__(self, key, counter_cached_interval=10):
        self.key = BitArray(uint=key, length=self.KEY_LENGTH)
        self.gen = DES.new(self.key.bytes)

        # cache for `_get_block`
        self._cache = dict()

        # cache for `count`
        # _counter_cache[index] will store the number of ones
        # before `index` * `_counter_cached_interval`
        self._counter_cached_interval = counter_cached_interval
        self._counter_cache = [0]

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = 0 if key.start is None else key.start
            end = key.stop
            step = 1 if key.step is None else key.step
            if step != 1:
                raise NotImplemented()
            start_index, start_offset = self._div_into_block(start)
            end_index, end_offset = self._div_into_block(end)

            # first block
            slc = self._get_block(start_index)
            if start_index == end_index:
                # all bits in one block
                return slc[start_offset: end_offset]
            else:
                slc = slc[start_offset:]
                for i in range(start_index + 1, end_index):
                    slc = slc + self._get_block(i)
                return slc + self._get_block(end_index)[:end_offset]

        block_index, offset = self._div_into_block(key)
        block = self._get_block(block_index)
        return int(block[offset])

    def _div_into_block(self, index):
        '''
        return index of block and offset in block
        '''
        return index // self.STRING_LENGTH, index % self.STRING_LENGTH

    def _get_block(self, index):
        if index not in self._cache:
            # bytes must conserve more space than BitArray
            self._cache[index] = self.gen.encrypt(
                BitArray(uint=index, length=self.STRING_LENGTH).bytes)
        return BitArray(bytes=self._cache[index])

    def count(self, value, start, length):
        '''
        Return count of total number of either zero of one bits
        from `start` to (`start` + `length` - 1)

        value -- if zero then count zero then count one
        '''
        end = start + length
        if value == 0:
            # convert counting for zero to counting for one
            return length - self.count(1, start, length)
        interval = self._counter_cached_interval
        while (len(self._counter_cache) - 1)* interval < end:
            now_length = len(self._counter_cache)
            now = self._counter_cache[-1]
            self._counter_cache.append(
                now + self[(now_length-1)*interval:now_length*interval].count(1)
            )
        cached_start = start // interval
        cached_end = end // interval
        ret = self._counter_cache[cached_end] - self._counter_cache[cached_start]
        ret = ret - self[cached_start * interval: start].count(1)
        ret = ret + self[cached_end * interval: end].count(1)
        return ret


class RandomPermuter(object):
    '''
    Used to randomly Permute sequence of number.

    Example:
        >>> rp = RandomPermuter(key=543252234, start=20, length=50)
        >>> rp.permute(532)
        123
    '''
    def __init__(self, key, length, start=0, counter_cached_interval=10):
        self.random_bits = RandomBits(key, counter_cached_interval)
        self.start = start
        self.length = length

    def test_input(self, value):
        if not self.start <= value < self.start+self.length:
            raise InputNotInRange()

    def _permute(self, x, alpha, length, d):
        if length == 1:
            return alpha
        if self.random_bits[d * length + alpha + x] == 0:
            return self._permute(
                self.random_bits.count(0, d * length + alpha, x),
                alpha,
                self.random_bits.count(0, d * length + alpha, length),
                d + 1)
        else:
            return self._permute(
                self.random_bits.count(1, d * length + alpha, x),
                alpha + self.random_bits.count(0, d * length + alpha, length),
                self.random_bits.count(1, d * length + alpha, length),
                d + 1)

    def permute(self, value):
        self.test_input(value)
        random_offset = self._permute(value - self.start, 0, self.length, 0)
        return self.start + random_offset


if __name__ == '__main__':
    from random import random

    for N in range(3, 10):
        end = 10 ** N
        start = 10 ** (N - 1)
        length = end - start

        rp = RandomPermuter(1008611, end - start, start, 500)

        print('First time')
        start_t = datetime.now()
        rp.permute(int(random() * length) + start)
        end_t = datetime.now()
        print('%d bit permuted takes %s' % (N, end_t - start_t))

        print('Next one hundred times')
        start_t = datetime.now()
        for i in range(100):
            rp.permute(int(random() * length) + start)
        end_t = datetime.now()
        print('%d bit permuted takes %s' % (N, end_t - start_t))
        print('\n')
