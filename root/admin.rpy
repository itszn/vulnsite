from twisted.web import resource,server
from twisted.internet import reactor

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate, AlertTemplate
import globalVals
import cgi
import json
import shutil

startSession()

class AdminView(Element):
    loader = XMLFile(FilePath('templates/adminView.xml'))

    def __init__(self, alert=None):
        Element.__init__(self)
        self.alert = alert

    @renderer
    def alertTag(self, req, tag):
        if self.alert==None:
            return tag('')
        cn = 'danger' if self.alert[0]==0 else 'success'
        return AlertTemplate(cn,self.alert[1])

class AdminViewFail(Element):
    loader = XMLFile(FilePath('templates/adminViewFail.xml'))

    def __init__(self):
        Element.__init__(self)

class AdminPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if not user.loggedIn:
            req.redirect('/')
            return ''

        if user.permission!=2:
            writeTemplate(
                MainTemplate("Admin Settings", user, AdminViewFail()),
                req
            )
            return server.NOT_DONE_YET

        

        alert = None
        if 'fail' in req.args:
            alert = (0, "Could not login")
        elif 'reg' in req.args:
            alert = (1, "You have been registered, now login!")
        writeTemplate(
            MainTemplate("Login", user, AdminView(alert)),
            req
        )
        return server.NOT_DONE_YET

    def render_POST(self, req):
        sess = req.getSession()
        user = IUser(sess)

        if not user.loggedIn:
            req.redirect('/')
            return ''

        alert = None
        if 'reloadConfig' in req.args:
            reactor.callFromThread(reloadConfig, user, req)
            return server.NOT_DONE_YET
        
        if not 'file' in req.args or len(req.args['file'])<1 or req.args['file'][0]=='':
            alert = (0, "You must actually upload a file")
        elif not 'filename' in req.args or len(req.args['filename'])<1 or req.args['filename'][0]=='':
            alert = (0, "You must have a valid file name")
        else:
            img = cgi.FieldStorage(
                fp = req.content,
                headers = req.getAllHeaders(),
                environ = {'REQUEST_METHOD':'POST',
                'CONTENT_TYPE': req.getAllHeaders()['content-type']}
            )
            try:
                name = '/uploads/'+req.args['filename'][0]
                f = open('root'+name,'wb')
                f.write(img['file'].value)
                f.close()
                globalVals.db.setMeme(name)

                alert = (1, "Successfully uploaded your meme!")
            except Exception as e:
                alert = (0, "Could not upload meme: Error = %s"%e)





        writeTemplate(
            MainTemplate("Admin Settings", user, AdminView(alert)),
            req
        )
        return server.NOT_DONE_YET

def reloadConfig(user, req):
    alert = None
    with open("root/config/admin.config","r") as f:
        try:
            conf = json.loads(f.read())
            conf['startingPoints'] = eval(conf.get('startingPoints',0))
            alert = (1, "Conf = %s"%json.dumps(conf))
            try:
                conf['startingPoints'] = int(conf.get('startingPoints',0))
            except:
                conf['startingPoints'] = 0
            globalVals.config = conf


        except Exception as e:
            alert = (0, "Unable to parse config (reverting to default): Error = %s"%e)
            f.close()
            shutil.copyfile('admin.config','root/config/admin.config')

            
    reactor.callFromThread(writeTemplate, MainTemplate("Admin settings", user, AdminView(alert)), req)


resource = AdminPage()
