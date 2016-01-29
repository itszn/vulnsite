import json
import time
import re

from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

import mainserver
import globalVals

#from templateManager import writeTemplate, MainTemplate
#import globalVals

class Api(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        mainserver.startSession()

    def getChild(self, name, req):
        return self

    def render_GET(self, req):
        sess = req.getSession()
        user = mainserver.IUser(sess)
        
        apiurl = req.path.strip('/').split('/')[1:]
        if apiurl[:1]==['logout']:
            user.loggedIn = False
            req.redirect('/')
        elif apiurl[:3]==['post','comment','add']:
            return self.addComment(req, user)

        return json.dumps({'error':'Invalid request'})

    def render_POST(self, req):
        sess = req.getSession()
        user = mainserver.IUser(sess)

        apiurl = req.path.strip('/').split('/')[1:]
        if apiurl[:1]==['login']:
            return self.login(req, user)
        elif apiurl[:1]==['register']:
            return self.register(req, user)
        elif apiurl[:2]==['post','submit']:
            return self.submitPost(req, user)
        elif apiurl[:2]==['post','vote']:
            return self.addVote(req, user, False)
        elif apiurl[:3]==['post','comment','vote']:
            return self.addVote(req, user, True)   
        elif apiurl[:2]==['message','send']:
            return self.sendMessage(req, user) 
        elif apiurl[:2]==['post','share']:
            return self.sharePost(req, user)
        elif apiurl[:3]==['post','link','submit']:
            return self.sendLink(req, user)
        elif apiurl[:4]==['moderator','message','send','format']:
            return self.addRawMessage(req, user)
        elif apiurl[:4]==['admin','post','format']:
            return self.submitRawPost(req, user)
        return json.dumps({'error':'Invalid request'})

    def login(self, req, user):
        if not 'name' in req.args or not 'pass' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if not globalVals.db.authenticateUser(req.args['name'][0],req.args['pass'][0]):
            return json.dumps({'error':'Could not log you in'})
        user.loggedIn = True
        globalVals.db.populateUser(req.args['name'][0],user)
        return json.dumps({'success':'true'})

    def register(self, req, user):
        if not 'name' in req.args or not 'pass' in req.args or not 'passCom' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if req.args['pass'][0]!=req.args['passCom'][0]:
            return json.dumps({'error':'Password does not match'})
        if req.args['name'][0]=='':
            return json.dumps({'error':'Username cannot be empty'})
        if req.args['pass'][0]=='':
            return json.dumps({'error':'Password cannot be empty'})
        if len(req.args['name'][0])>30:
            return json.dumps({'error':'Username must be at most 30 characters'})
        if globalVals.db.addUser(req.args['name'][0],req.args['pass'][0])==None:
            return json.dumps({'error':'Username already taken'})
        print '%s registered an account'%req.args['name'][0]
        return json.dumps({'success':'true'})

    def submitPost(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if not 'title' in req.args or not 'body' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if req.args['title'][0]=='':
            return json.dumps({'error':'Title cannot be empty'})
        post = globalVals.db.addPost(user, req.args['title'][0], req.args['body'][0])
        print '%s added a post'%user.userName
        return json.dumps({'success':'true','post':post})

    def submitRawPost(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if not user.permission>1:
            return json.dumps({'error':'Only admins may use this...'})
        if not 'title' in req.args or not 'body' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if req.args['title'][0]=='':
            return json.dumps({'error':'Title cannot be empty'})
        post = globalVals.db.addPost(user, req.args['title'][0], req.args['body'][0], raw=True)
        print '%s added a raw post'%user.userName
        return json.dumps({'success':'true','post':post})

    def addComment(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})

        if not 'id' in req.args or not 'body' in req.args:
            return json.dumps({'error':'Missing arguments'})
        try:
            postId = int(req.args['id'][0])
        except Exception as e:
            return json.dumps({'error':'Bad id'})
        if req.args['body'][0]=='':
            return json.dumps({'error':'Body cannot be empty'})
        if not globalVals.db.addComment(user, postId, req.args['body'][0]):
            return json.dumps({'error':'Post not found'})
        print '%s added a comment'%user.userName

        return json.dumps({'success':'true','post':postId})

    def addVote(self, req, user, isComment):
        if not user.loggedIn:
            return json.dumps({'error':'Not logged in'})
        if not 'id' in req.args or not 'way' in req.args:
            return json.dumps({'error':'missing id'})
        try:
            way = int(req.args['way'][0])
            postId = int(req.args['id'][0]) if not isComment else None
            commentId = int(req.args['id'][0]) if isComment else None
        except Exception as e:
            return json.dumps({'error':'Invalid id'})
        
        if (postId!=None and postId<1) or (commentId!=None and commentId<1):
            return json.dumps({'error':'Invalid id'})

        cv = globalVals.db.getVote(user, postId, commentId)
        if cv==way:
            return json.dumps({'error':'Already voted that way'})

        
        if not globalVals.db.addVote(user, way, cv, postId, commentId):
            return json.dumps({'error':'Error voting'})

        return json.dumps({'success':'true'})

    def sendMessage(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if (not 'id' in req.args and not 'username' in req.args) or not 'body' in req.args:
            return json.dumps({'error':'Missing arguments'})
        try:
            userId = int(req.args['id'][0]) if 'id' in req.args else None
        except Exception as e:
            return json.dumps({'error':'Bad user id'})

        if req.args['body'][0]=='':
            return json.dumps({'error':'Body cannot be null'})

        if userId == None:
            if not 'username' in req.args:
                return json.dumps({'error':'Missing name'})
            userId = globalVals.db.getUserIdByName(req.args['username'][0])
            if userId==None:
                return json.dumps({'error':'Could not find user'})

        if not globalVals.db.sendMessage(user, userId, req.args['body'][0]):
            return json.dumps({'error':'User does not exist'})
        if globalVals.sim.admin.userId==userId:
            globalVals.sim.adminRespond(user)
        print '%s sent a message to %s'%(user.userName,
            req.args['username'][0] if 'username' in req.args else str(userId))
        return json.dumps({'success':'true','user':userId})


    def addRawMessage(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if not user.permission>0:
            return json.dumps({'error':'Only moderators+ may use this...'})
        if not 'username' in req.args or not 'body' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if req.args['body'][0]=='':
            return json.dumps({'error':'Body cannot be null'})

        if re.search('< *script.*>',req.args['body'][0],re.I)!=None:
            return json.dumps({'error':'No script tags allowed'})

        userId = globalVals.db.getUserIdByName(req.args['username'][0])
        if userId==None:
            return json.dumps({'error':'Could not find user'})
        if not globalVals.db.sendMessage(user, userId, req.args['body'][0],raw=True):
            return json.dumps({'error':'User does not exist'})
        print "Sending raw message"
        if globalVals.sim.admin.userId==userId:
            globalVals.sim.adminRespond(user)
        print '%s sent a raw message to %s'%(user.userName,
            req.args['username'][0] if 'username' in req.args else str(userId))
        return json.dumps({'success':'true','user':userId})


    def sharePost(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if not 'postId' in req.args or not 'username' in req.args:
            return json.dumps({'error':'Missing arguments'})
        try:
            postId = int(req.args['postId'][0])
        except Exception as e:
            return json.dumps({'error':'Bad post id'})

        userId = globalVals.db.getUserIdByName(req.args['username'][0])
        if userId==None:
            return json.dumps({'error':'Could not find user'})

        post = globalVals.db.getPostById(postId)
        if post==None:
            return json.dumps({'error':'Could not find post'})

        if post['permission']>user.permission:
            return json.dumps({'error':'You do not have permission to access that post'})

        body = '%s wanted to share this post with you:\nTitle: %s\nBody: %s\nBy %s at %s'%(
            user.userName, post['title'], post['body'], post['userName'],
            time.strftime('%H:%M %m/%d',time.localtime(post['time']))
        )
        globalVals.db.sendMessage(user, userId, body)
        print '%s shared a post with %s'%(user.userName,
            req.args['username'][0] if 'username' in req.args else str(userId))
        return json.dumps({'success':'true'})

    def sendLink(self, req, user):
        if not user.loggedIn:
            return json.dumps({'error':'Please login first.'})
        if not 'title' in req.args or not 'url' in req.args:
            return json.dumps({'error':'Missing arguments'})
        if req.args['title'][0]=='':
            return json.dumps({'error':'Title cannot be empty'})
        if req.args['url'][0]=='':
            return json.dumps({'error':'Url cannot be empty'})

        if globalVals.db.didUserSendLink(user.userId):
            return json.dumps({'error':'You are sending links too fast! Please wait a few seconds.'})
        globalVals.sim.visitLink(user.userId, req.args['url'][0])
        globalVals.db.setUserSentLink(user.userId, True)
        return json.dumps({'success':'true','info':'The moderator will check your link soon!'})
