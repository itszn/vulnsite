from twisted.web import server, resource, static, script

import mainserver

class FileNoList(static.File):
    pass
    #def directoryListing(self):
    #    return self.childNotFound
