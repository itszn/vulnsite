import time
from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate
import globalVals

class PostView(Element):
    loader = XMLFile(FilePath('templates/postView.xml'))

    def __init__(self, user, page=1):
        Element.__init__(self)
        self.user = user
        self.page = page

    @renderer
    def postPanel(self, req, tag):
        posts = globalVals.db.getPostsByRating(self.page)
        if len(posts)==0:
            tag.clear()
            yield 'No posts here...'
        for p in posts:
            vote = globalVals.db.getVote(self.user,p['id'])
            nt = tag.clone().fillSlots(
                postLink="/post?id=%u"%p['id'],
                title=p['title'],
                profileLink="/user?id=%u"%p['user'],
                userName=p['userName'],
                numComments=str(p['numComments']),
                points=str(p['points']),
                timestamp=time.strftime('%H:%M %m/%d',time.localtime(p['time'])),
                postId=str(p['id']),
                upVoteClassName='glyphicon glyphicon-triangle-top vote upvote' + (' active' if vote>0 else ''),
                downVoteClassName='glyphicon glyphicon-triangle-bottom vote downvote' + (' active' if vote<0 else '')
            )
            yield nt
    @renderer
    def pageNums(self, req, tag):
        tag.fillSlots(
            page=str(self.page) if self.page!=None else 'What',
            backlink="/?page=%u"%(self.page-1 if self.page>1 else 1),
            forlink="/?page=%u"%(self.page+1),
            backclass="disabled" if self.page==1 else ""
        )
        return tag

class IndexPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)

        try:
            page = int(req.args['page'][0]) if 'page' in req.args else 1
            page = 1 if page<1 else page
        except Exception as e:
            page = 1
        
        writeTemplate(
            MainTemplate("Beddit", user, PostView(user,page)),
            req
        )
        return server.NOT_DONE_YET

resource = IndexPage()