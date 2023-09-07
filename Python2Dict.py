DK_SIZE = 8
PERTURB_SHIFT = 5

class Python2Dict(dict):
    def iterkeys(self):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L364-L366
        mask = self._get_mask()
        hashdict = {}
        for k in self:
            hash_val = hash(k)
            hash_idx = self._get_hashindex(hash_val, mask)

            if hash_idx in hashdict:
                perturb = hash_val
                while True:
                    hash_idx = self._get_linearprobing(hash_idx, perturb, mask)
                    if hash_idx not in hashdict:
                        break
                    perturb = perturb >> PERTURB_SHIFT
        
            hashdict[hash_idx] = k

        return [hashdict[i] for i in sorted(hashdict)].__iter__()
    
    def itervalues(self):
        return [self[i] for i in self.iterkeys()].__iter__()
    
    def _get_hashindex(self, hash, mask):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L331
        return hash & mask
    
    def _get_linearprobing(self, hashindex, perturb, mask):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L365
        return (hashindex * 5 + perturb + 1) & mask
    
    def _get_dksize(self):
        #https://github.com/python/cpython/blob/v2.7.12/Objects/dictobject.c#L802-L819
        length = len(self)
        size_coeff = 4
        count = 0
        if length > 50000:
            size_coeff = 2
        while True:
            new_size = DK_SIZE * (size_coeff ** count)
            if (length * 3) < (new_size * 2):
                return new_size
            count += 1

    def _get_mask(self):
        return self._get_dksize() - 1