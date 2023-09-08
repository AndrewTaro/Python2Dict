DK_SIZE = 8
PERTURB_SHIFT = 5

class Python2Dict(dict):
    def iterkeys(self):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L364-L366
        hashtable = {}
        count = 0
        while len(hashtable) < len(self):
            size = self.__get_dksize(hashtable)
            mask = size - 1
            temptable = {}
            used_keys = set()

            for hashkey in sorted(hashtable): #preseiving the hash order before resizing
                key = hashtable[hashkey]
                hash_idx = self._get_hashindex(key, mask, temptable)
                used_keys.add(key)
                temptable[hash_idx] = key

            for key in self: #preserving the order of insertion
                if key in used_keys:
                    continue
                hash_idx = self._get_hashindex(key, mask, temptable)
                temptable[hash_idx] = key
                if len(temptable)*3 >= size*2: #need resize
                    break
            count += 1
            hashtable = temptable

        for hashkey in sorted(hashtable):
            yield hashtable[hashkey]
    
    def itervalues(self):
        for i in self.iterkeys():
            yield self[i]
    
    def iteritems(self):
        for i in self.iterkeys():
            yield (i, self[i])
    
    def _get_hashindex(self, key, mask, hashtable):
        """
        calculates index in the hashtable from key, current dict size and hashtable.
        """
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L364-L366
        hash_val = hash(key)
        hash_idx = self.__apply_mask(hash_val, mask)

        if hash_idx in hashtable:
            perturb = hash_val
            while True:
                hash_idx = self.__apply_linearprobing(hash_idx, perturb, mask)
                if hash_idx not in hashtable:
                    break
                perturb = perturb >> PERTURB_SHIFT
    
        return hash_idx
    
    def __apply_mask(self, hash, mask):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L331
        return hash & mask
    
    def __apply_linearprobing(self, hashindex, perturb, mask):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L365
        return (hashindex * 5 + perturb + 1) & mask
    
    def __get_dksize(self, dict):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L802-L819
        length = len(dict)
        size_coeff = 4
        count = 0
        if length > 50000:
            size_coeff = 2
        while True:
            size = DK_SIZE * (size_coeff ** count)
            if (length * 3) < (size * 2):
                return size
            count += 1

    def __get_mask(self, size):
        return size - 1