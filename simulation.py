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
        globalVals.db.addUser('admin',ADMIN_PASS,2)
        self.getUsers()

        globalVals.db.addPost(self.admin,'Welcome','<h3>Welcome to Beddit</h3>Beddit is the better reddit.\nPlease read the sidebar before posting.\n<i>Thanks</i>\n-<b><font color="red">Admin</font></b>')
        globalVals.db.addPost(self.mod,'Note to self: Moderator api',"""This is a reminder to me and the admin of how the mod APIs work.
Use POST to /api/moderator/message/send/format with 'username' and 'body' to send a private message with HTML formating. No <script> tags allowed.

Admin can POST to /api/admin/post/format with 'title' and 'body' to create a post with HTML formating.
Thats all for now.""",1)

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
            "Thanks for the message.\n<b><font color=\"red\">ADMIN</font>",raw=True)
