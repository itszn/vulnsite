from twisted.web import server, resource, static, script

import mainserver

class FileNoList(static.File):
    def directoryListing(self):
        return self.childNotFound