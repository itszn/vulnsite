from twisted.web.template import Element, renderer, XMLFile,XMLString
from twisted.python.filepath import FilePath
from twisted.web.template import flattenString

import globalVals

def reqWriteCallback(data, req):
    req.write(data)
    req.finish()

def writeTemplate(template, request):
    flattenString(request, template).addCallback(reqWriteCallback, request)

class MainTemplate(Element):
    loader = XMLFile(FilePath('templates/main.xml'))

    def __init__(self, title, user, body=None):
        Element.__init__(self)
        self.titleText = title
        self.user = user
        self.bodyElement = body

    @renderer
    def body(self, req, tag):
        if self.bodyElement==None:
            return tag('No content on this page sorry...')
        return self.bodyElement

    @renderer
    def titleTag(self, req, tag):
        return tag(self.titleText)

    @renderer
    def userSpot(self, req, tag):
        if self.user!=None and self.user.loggedIn:
            return UserInfoTemplate(self.user)
        return RawXML('<ul class="nav navbar-nav navbar-right"><li><a href="/login">Login</a></li><li><a href="/register">Register</a></li></ul>')

class RawXML(Element):
    def __init__(self, data):
        self.loader = XMLString(data)
        Element.__init__(self)

class UserInfoTemplate(Element):
    loader = XMLFile(FilePath('templates/userInfoView.xml'))

    def __init__(self, user):
        Element.__init__(self)
        self.user = user

    @renderer
    def userInfo(self, req, tag):
        notes,points = globalVals.db.getNumNotifsForUser(self.user.userId)
        cn = 'active' if notes>0 else ''
        tag.fillSlots(
            name=self.user.userName,
            points=str(points),
            notes=str(notes),
            link='/user?id=%u'%self.user.userId,
            className=cn
        )
        return tag

class AlertTemplate(Element):
    loader = XMLFile(FilePath('templates/alert.xml'))

    def __init__(self, alertType, text):
        Element.__init__(self)
        self.alertType = alertType
        self.alertText = text

    @renderer
    def alertTag(self, req, tag):
        return tag.fillSlots(
            alertClass='alert alert-'+self.alertType,
            alertText=self.alertText
        )