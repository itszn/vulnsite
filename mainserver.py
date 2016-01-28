import os
import pwd
import grp
import argparse

from twisted.web import server, resource, static, script
from twisted.internet import reactor

from zope.interface import Interface, Attribute, implements
from twisted.python.components import registerAdapter
from twisted.web.server import Session

import globalVals
import staticFiles
import api

class IUser(Interface):
    loggedIn = Attribute("Is the user logged in")
    userId = Attribute("Id of the user")
    userName = Attribute("Username")
    permission = Attribute("User's permission mode")

    _points = Attribute("Private points")
    points = Attribute("Real points")

class User(object):
    def __init__(self, sess):
        self.loggedIn = False

startedSession = False

def startSession():
    global startedSession
    if not startedSession:
        print "Started session adapter"
        registerAdapter(User, Session, IUser)
        startedSession = True

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)

def startServer():
    ap = argparse.ArgumentParser(description='Server options')
    ap.add_argument('--clean',action='store_true',default=False)
    ap.add_argument('--port',type=int,default=1337)
    ap.add_argument('--domain',default='192.168.220.130')

    args = ap.parse_args()


    root = staticFiles.FileNoList('root')
    root.indexNames = ['index.rpy']
    root.ignoreExt('.rpy')
    root.processors = {'.rpy': script.ResourceScript}
    root.putChild('api',api.Api())

    globalVals.init(args,root)

    site = server.Site(root, logPath=b"access.log")
    reactor.listenTCP(args.port, site)
    drop_privileges('rpisec','rpisec')
    reactor.run()

if __name__ == "__main__":
    startServer()
    