from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate, AlertTemplate
import globalVals

startSession()

class RegisterView(Element):
    loader = XMLFile(FilePath('templates/registerView.xml'))

    def __init__(self, alert=None):
        Element.__init__(self)
        self.alert = alert

    @renderer
    def alertTag(self, req, tag):
        if self.alert==None:
            return ''
        return AlertTemplate('danger',self.alert)

class RegisterPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if user.loggedIn:
            req.redirect('/')
            return ''

        alert = "Invalid username" if 'fail' in req.args else None

        writeTemplate(
            MainTemplate("Login", user, RegisterView(alert)),
            req
        )
        return server.NOT_DONE_YET

resource = RegisterPage()