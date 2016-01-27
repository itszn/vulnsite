import subprocess
import time

from twisted.internet import reactor

import mainserver
import globalVals

MODERATOR_PASS = '49e834007bd16087601dbc6c603dd2505eb2dabcc57a1f60860dff900251b94d'
ADMIN_PASS = '49e834007bd16087601dbc6c603dd2505eb2dabcc57a1f60860dff900251b94d'


class Simulation():
    def __init__(self, clean=False):
        if clean:
            self.clean()
        else:
            self.getUsers()

    def clean(self):
        globalVals.db.addUser('moderator',MODERATOR_PASS,1)
        globalVals.db.addUser('admin',ADMIN_PASS,1)
        self.getUsers()

        globalVals.db.addPost(self.admin,'Welcome','Welcome to beddit, the better reddit.\nPlease read the sidebar before posting.\nThanks\n-Admin')
        globalVals.db.addPost(self.mod,'Mod test 2','Note to self. Moderator api access',1)

    def getUsers(self):
        self.mod = mainserver.User(None)
        globalVals.db.populateUser('moderator',self.mod)
        self.mod.loggedIn = True

        self.admin = mainserver.User(None)
        globalVals.db.populateUser('admin',self.admin)
        self.admin.loggedIn = True
        
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
        globalVals.db.sendMessage(self.mod, uid, 
            "<b>Hello</b>\nThank you for submitting your link.\nI looked at your it, but do not feel that it is worthy of being posted to the site.\nSorry.\n-<b><font color=\"green\">MODERATOR</font></b>",raw=True)

    def adminRespond(self, user):
        reactor.callInThread(self.spawnAdmin, user)

    def spawnAdmin(self, user):
        if user.permission==0:
            time.sleep(5)
        else:
            proc = subprocess.Popen(['phantomjs', 'phantom/checkMessages.js',
                globalVals.args.domain+':'+str(globalVals.args.port), ADMIN_PASS],
                stdout=subprocess.PIPE
            )
            log,_ = proc.communicate()
            print log
            f = open('phantom/messages.log','a')
            f.write(log)
            f.close()
            time.sleep(5)

        reactor.callFromThread(self.adminSendResponse, user)

    def adminSendResponse(self, user):
        globalVals.db.sendMessage(self.admin, user.userId,
            "Test\n<b><font color=\"red\">ADMIN</font>",raw=True)
