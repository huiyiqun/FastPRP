# from bitstring import BitArray
from Crypto.Cipher import DES
from datetime import datetime
from functools import wraps
from convert import bytes2bools, uint2bytes, uint2bools
from exception import InputNotInRange


def cached(f):
    @wraps(f)
    def g(*args, **kwargs):
        if g.ret is None:
            ret = f(*args, **kwargs)
        return ret
    g.ret = None
    return g


#def uint2bytes(uint, length):
    #ret = [0] * length
    #for i in range(length):
        #ret[i] = uint & 255
        #uint >>= 8
        #if uint == 0:
            #break
    #else:
        #print(uint, length)
        #raise InputNotInRange()
    #return bytes(reversed(ret))


#def uint2bools(uint, length):
    #ret = [False] * length
    #for i in range(length):
        #ret[i] = (uint & 1 == 1)
        #uint >>= 1
        #if uint == 0:
            #return ret
    #raise InputNotInRange()


#def bytes2bools(bytes):
    #ret = []
    #for b in reversed(bytes):
        #single_byte = [False] * 8
        #for i in range(8):
            #single_byte[i] = (b & 1 == 1)
            #b >>= 1
            #if b == 0:
                #break
        #ret += single_byte
    #return ret


class BitArray(object):
    '''
    For BitArray from bitstring is not efficient,
    I try to re-implement a version with same interface
    but less functions.

    Note:
        This object is readonly, that is, never change the
        content after initialization.
    '''
    def __init__(self, length=None, uint=None, bytes=None, _data=None):
        if uint is not None and length is not None:
            self._data = uint2bools(uint, length)
        elif bytes is not None:
            self._data = bytes2bools(bytes)
        elif _data is not None:
            self._data = _data

        # tuple is readonly and not always copys itself when sliced
        # Maybe list is fast?
        self._data = tuple(self._data)
        self.length = len(self._data)

    @property
    @cached
    def bytes(self):
        point = 0
        ret = []
        while point < len(self._data):
            byte = self._data[point: point+8]
            value = 0
            step = 1
            for i in range(len(byte)):
                if byte[i]:
                    value += step
                step <<= 1
            ret.append(value)
            point += 8
        return bytes(reversed(ret))

    @property
    @cached
    def _count_one(self):
        return sum(self._data)

    def count(self, value):
        if value:
            return self._count_one
        else:
            return self.length - self._count_one

    def __getitem__(self, key):
        if isinstance(key, slice):
            return BitArray(_data=self._data[key])
        return self._data[key]

    def __add__(self, other):
        if isinstance(other, BitArray):
            return BitArray(_data=self._data+other._data)


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
            # but init BitArray with bytes is CPU-expensive
            block = self.gen.encrypt(
                uint2bytes(index, self.STRING_LENGTH >> 3))
            self._cache[index] = BitArray(bytes=block)
        return self._cache[index]

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
        while (len(self._counter_cache) - 1) * interval < end:
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

    for N in range(6, 10):
        end = 10 ** N
        start = 10 ** (N - 1)
        length = end - start

        rp = RandomPermuter(1008611, end - start, start, 10000)

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
