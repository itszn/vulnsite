import time
from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession, User
from templateManager import writeTemplate, MainTemplate
import globalVals

class UserView(Element):
    loader = XMLFile(FilePath('templates/userView.xml'))

    def __init__(self, user):
        Element.__init__(self)
        self.user = user

    @renderer
    def userInfo(self, req, tag):
        tUser = User(None)
        if not globalVals.db.populateUser(None, tUser, uid=req.args['id'][0]):
            tag.clear()
            return 'User not found...'
        tag.fillSlots(
            name=tUser.userName,
            points=str(tUser.points),
            status=['Normal User','Moderator','Admin'][tUser.permission],
            userId=str(tUser.userId)
        )
        return tag

    @renderer
    def loggedInTag(self, req, tag):
        if not self.user.loggedIn:
            tag.clear()
            return tag('Login to message this user')
        return tag

class UserPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if not 'id' in req.args:
            req.redirect('/')
            return ''

        writeTemplate(
            MainTemplate("User", user, UserView(user)),
            req
        )
        return server.NOT_DONE_YET

resource = UserPage()