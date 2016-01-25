

class Cache(object):
    def __init__(self):
        self.cacheVals = {}
        self.cacheValid = {}

    def cache(self, cid, data):
        self.cacheVals[cid] = data
        self.cacheValid[cid] = True

    def getCache(self, cid):
        if not cid in self.cacheVals:
            return None
        return self.cacheVals[cid]

    def invalidateCache(self, cid=None):
        if cid==None:
            self.cacheVals = {}
            self.cacheValid = {}
        else:
            if cid in self.cacheValid:
                self.cacheValid[cid] = {}
                self.cacheVals[cid] = None

    def isCacheValid(self, cid):
        if not cid in self.cacheValid:
            return False
        return self.cacheValid[cid]