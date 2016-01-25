import subprocess
import time

from twisted.internet import reactor

import mainserver
import globalVals

MODERATOR_PASS = '49e834007bd16087601dbc6c603dd2505eb2dabcc57a1f60860dff900251b94d'

class Simulation():
    def __init__(self, clean=False):
        if clean:
            self.clean()
        else:
            self.getUsers()

    def clean(self):
        self.mod = mainserver.User(None)
        globalVals.db.addUser('moderator',MODERATOR_PASS,1)
        self.getUsers()

        globalVals.db.addPost(self.mod,'Mod test','Mod test yo')
        globalVals.db.addPost(self.mod,'Mod test 2','Only mods can see this!',1)

    def getUsers(self):
        self.mod = mainserver.User(None)
        globalVals.db.populateUser('moderator',self.mod)
        self.mod.loggedIn = True
        
    def visitLink(self, uid, url):
        reactor.callInThread(self.spawnModerator, uid, url)

    def spawnModerator(self, uid, url):
        proc = subprocess.Popen(['phantomjs', 'phantom/checkLink.js',
            globalVals.args.domain+':'+str(globalVals.args.port), MODERATOR_PASS, str(uid), url],
            stdout=subprocess.PIPE
        )
        log,_ = proc.communicate()
        print log
        f = open('phantom/links.log','a')
        f.write(log)
        f.close()
        time.sleep(5)
        reactor.callFromThread(self.freeUserSentLink, uid)

    def freeUserSentLink(self, uid):
        globalVals.db.setUserSentLink(uid,False)
        globalVals.db.sendMessage(self.mod, uid, "I looked at your link, but do not feel that it is worthy of being posted. Sorry.")