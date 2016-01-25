from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate, AlertTemplate
import globalVals

class SubmitView(Element):
    loader = XMLFile(FilePath('templates/submitView.xml'))

    def __init__(self, alert=None):
        Element.__init__(self)
        self.alert = alert

    @renderer
    def alertTag(self, req, tag):
        if self.alert==None:
            return ''
        cn = 'danger' if self.alert[0]==0 else 'success'
        return AlertTemplate(cn,self.alert[1])

class SubmitPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if not user.loggedIn:
            req.redirect('/login')
            return ''

        alert = None
        if 'fail' in req.args:
            alert = (0, "Your post has problems")

        writeTemplate(
            MainTemplate("Submit", user, SubmitView(alert)),
            req
        )
        return server.NOT_DONE_YET

resource = SubmitPage()