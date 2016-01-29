import time
from twisted.web import resource,server

from twisted.web.template import Element, renderer, XMLFile,flattenString,tags
from twisted.python.filepath import FilePath

from mainserver import IUser, startSession
from templateManager import writeTemplate, MainTemplate, RawFormat
import globalVals

startSession()

class CommentView(RawFormat):
    loader = XMLFile(FilePath('templates/commentView.xml'))

    def __init__(self, user, post):
        Element.__init__(self)
        self.user = user
        self.post = post

    @renderer
    def postPanel(self, req, tag):
        p = self.post
        if p==None:
            tag.clear()
            return 'Sorry that post could not be found'
        vote = globalVals.db.getVote(self.user,p['id'])
        print p
        if not p['raw']==1:
            body = tags.p()
            for s in p['body'].split('\n'):
                body(s)
                body(tags.br)
        else:
            body = self.addFormat(p['body'].replace('\n','<br />'))
        nt = tag.fillSlots(
            title=p['title'],
            body=body,
            profileLink="/user?id=%u"%p['user'],
            userName=p['userName'],
            numComments=str(p['numComments']),
            points=str(p['points']),
            timestamp=time.strftime('%H:%M %m/%d',time.localtime(p['time'])),
            postId=str(p['id']),
            upVoteClassName='glyphicon glyphicon-triangle-top vote upvote' + (' active' if vote>0 else ''),
            downVoteClassName='glyphicon glyphicon-triangle-bottom vote downvote' + (' active' if vote<0 else '')
        )
        return nt

    @renderer
    def commentPanel(self, req, tag):
        comments = globalVals.db.getCommentsByRating(self.post['id'])
        if len(comments)==0:
            tag.clear()
            yield 'No comments yet. Be the first!'
        for c in comments:
            body = tags.p()
            for s in c['body'].split('\n'):
                body(s)
                body(tags.br)
            vote = globalVals.db.getVote(self.user,self.post['id'],c['id'])
            nt = tag.clone().fillSlots(
                body=body,
                profileLink="/user?id=%u"%c['user'],
                userName=c['userName'],
                timestamp=time.strftime('%H:%M %m/%d',time.localtime(c['time'])),
                points=str(c['points']),
                commentId=str(c['id']),
                postId=str(self.post['id']),
                upVoteClassName='glyphicon glyphicon-triangle-top comment vote upvote' + (' active' if vote>0 else ''),
                downVoteClassName='glyphicon glyphicon-triangle-bottom comment vote downvote' + (' active' if vote<0 else '')
            )
            yield nt

    @renderer
    def postId(self, req, tag):
        return str(self.post['id'])

    @renderer
    def addCommentPanel(self, req, tag):
        if not self.user.loggedIn:
            tag.clear()
            return 'Please login to add a comment'
        return tag

    @renderer
    def permission(self, req, tag):
        if self.post['permission']>0:
            if not self.user.loggedIn or self.user.permission<self.post['permission']:
                tag.clear()
                if self.post['permission']==1:
                    return tag('Sorry, only moderators+ can view this post.')
                return tag('Sorry, only admins+ can view this post.')
        return tag


class PostPage(resource.Resource):
    def render_GET(self, req):
        sess = req.getSession()
        user = IUser(sess)
        if not 'id' in req.args:
            req.redirect('/')
            return ''

        post = globalVals.db.getPostById(req.args['id'][0])
        if post==None:
            req.redirect('/')
            return ''
        
        rawView = CommentView(user, post)
        writeTemplate(
            MainTemplate("Beddit", user, rawView),
            req,
            rawView
        )
        return server.NOT_DONE_YET

resource = PostPage()