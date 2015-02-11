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
        self.keeped = keeped if keeped is not None else self._keeped
        self.width = width
        self.key = key
        self.random_permuters = dict()

    def _keeped(self, x):
        return False

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
    for N in range(3, 30):
        start_t = datetime.now()
        awrp = ArbitaryWidthRandomPermute(1008611, N)
        for i in range(100):
            awrp.permute(i)
        end_t = datetime.now()
        print('%d bit permuted (100 times) takes %s' % (N, end_t - start_t))

    # test validity
    test_bits = 5
    def test_validity(awrp, i, found):
        res = awrp.permute(i)
        #print('%d -->' % i, res)
        if res is None:
            return
        if found:
            if hasattr(found, 'lock'):
                with found.lock:
                    if res in found:
                        raise Exception('Output is not unique')
                    found.add(res)
                    #print('Length of found is %d.' % len(found))
            else:
                if res in found:
                    raise Exception('Output is not unique')
                found.add(res)
                #print('Length of found is %d.' % len(found))
        if not 10 ** (test_bits-1) <= res < 10 ** test_bits:
            raise Exception('Output is not in given range')

    # single thread
    start_t = datetime.now()
    awrp = ArbitaryWidthRandomPermute(1008611, test_bits)
    found = set()
    for i in range(10 ** test_bits):
        test_validity(awrp, i, found)
    end_t = datetime.now()
    print('%d unique number generated.' % len(found))
    print('it takes %s' % (end_t - start_t))

    # multithreading
    # Because of GIL, multithread gain no efficency.
    # whatever, this module is thread-safe.
    from threading import Thread, Lock
    start_t = datetime.now()
    awrp = ArbitaryWidthRandomPermute(1008611, test_bits)
    class set(set, object):
        pass
    found = set()
    found.lock = Lock()
    threads = list()
    for i in range(10 ** test_bits):
        t = Thread(target=test_validity, args=(awrp, i, found))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_t = datetime.now()
    print('%d unique number generated.' % len(found))
    print('it takes %s' % (end_t - start_t))

    # multiprocess
    def test_validity_with_shared_memory(args):
        shared, lock, r2s, i = args
        # get the object from proxy, then notify the change
        awrp = shared.awrp
        res = awrp.permute(i)
        shared.awrp = awrp
        #print('%d -->' % i, res)
        if res is None:
            return
        with lock:
            if res in found:
                raise Exception('Output is not unique')
            found[res] = i
            #print('Length of found is %d.' % len(found))

        if not 10 ** (test_bits-1) <= res < 10 ** test_bits:
            raise Exception('Output is not in given range')


    from multiprocessing import Pool, Manager, Lock
    start_t = datetime.now()
    mgr = Manager()
    shared = mgr.Namespace()
    shared.awrp = ArbitaryWidthRandomPermute(1008611, test_bits)
    result_to_source = mgr.dict()
    lock = mgr.Lock()
    pool = Pool(processes=8)
    pool.map(test_validity_with_shared_memory, ((shared, lock, result_to_source, i) for i in range(10 ** test_bits)))
    pool.close()
    pool.join()
    end_t = datetime.now()
    print('%d unique number generated.' % len(shared.found))
    print('it takes %s' % (end_t - start_t))
