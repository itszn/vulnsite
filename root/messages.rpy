import time
from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString,tags
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession, User
from templateManager import writeTemplate, MainTemplate, RawFormat
import globalVals

class MessagesView(RawFormat):
    loader = XMLFile(FilePath('templates/messageView.xml'))

    def __init__(self, user):
        Element.__init__(self)
        self.user = user

    @renderer
    def messagePanel(self, req, tag):
        messages = globalVals.db.getMessages(self.user)
        globalVals.db.clearNotifsForUser(self.user.userId)

        if len(messages)==0:
            tag.clear()
            yield "Sorry, no messages yet."
        
        for m in messages:
            if not m['raw']==1:
                body = tags.p()
                for s in m['body'].split('\n'):
                    body(s)
                    body(tags.br)
            else:
                body = self.addFormat(m['body'].replace('\n','<br />'))

            nt = tag.clone().fillSlots(
                body=body,
                userName=m['fromName'],
                profileLink='/user?id=%u'%m['from'],
                timestamp=time.strftime('%H:%M %m/%d',time.localtime(m['time'])),
            )
            yield nt

class MessagesPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if not user.loggedIn:
            req.redirect('/login')
            return ''
        

        rawView = MessagesView(user)
        writeTemplate(
            MainTemplate("Messages", user, rawView),
            req,
            rawView
        )
        return server.NOT_DONE_YET

resource = MessagesPage()