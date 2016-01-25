from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate, AlertTemplate
import globalVals

startSession()

class LoginView(Element):
    loader = XMLFile(FilePath('templates/loginView.xml'))

    def __init__(self, alert=None):
        Element.__init__(self)
        self.alert = alert

    @renderer
    def alertTag(self, req, tag):
        if self.alert==None:
            return tag('')
        cn = 'danger' if self.alert[0]==0 else 'success'
        return AlertTemplate(cn,self.alert[1])

class LoginPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if user.loggedIn:
            req.redirect('/')
            return ''

        alert = None
        if 'fail' in req.args:
            alert = (0, "Could not login")
        elif 'reg' in req.args:
            alert = (1, "You have been registered, now login!")

        writeTemplate(
            MainTemplate("Login", user, LoginView(alert)),
            req
        )
        return server.NOT_DONE_YET

resource = LoginPage()