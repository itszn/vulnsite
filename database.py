import os
import time
import json
import random
import sqlite3
import hashlib

import globalVals

class Database(object):
    def __init__(self, clean=False):
        self.conn = sqlite3.connect('sql/database.db')
        self.cur = self.conn.cursor()
        if clean:
            self.clean()

    def mapCols(self, data):
        obj = {}
        cols = self.cur.description
        for i,d in enumerate(data):
            obj[cols[i][0]] = d
        return obj

    def clean(self):
        print "Cleaning!"
        self.conn.close()
        if os.path.isfile('sql/database.db'):
            os.unlink('sql/database.db')
        self.conn = sqlite3.connect('sql/database.db')
        self.cur = self.conn.cursor()

        template = open('sql/tables.sql')
        self.cur.executescript(template.read())
        template.close()

        self.conn.commit()

    def addUser(self, name, password, permission=0):
        taken = self.cur.execute("SELECT `id` FROM `user` WHERE `name`=?",(name,)).fetchone()
        if taken!=None:
            return None
        
        salt = '%016x'%random.getrandbits(64)
        passhash = hashlib.sha256()
        passhash.update(salt)
        passhash.update(password)
        passhash = passhash.hexdigest()

        self.cur.execute("INSERT INTO `user` (`name`,`salt`,`pass`,`permission`) VALUES (?,?,?,?)",
            (name, salt, passhash,permission,))
        self.conn.commit()
        return self.cur.lastrowid

    def authenticateUser(self, name, password):
        user = self.cur.execute("SELECT `salt`,`pass` FROM `user` WHERE `name`=?",
            (name,)).fetchone()
        if user==None:
            return False
        passhash = hashlib.sha256()
        passhash.update(user[0])
        passhash.update(password)
        passhash = passhash.hexdigest()
        return passhash==user[1]

    def populateUser(self, name, user,uid=None):
        if uid==None:
            data = self.cur.execute("SELECT `id`,`name`,`points`,`permission` FROM `user` WHERE `name`=?",
                (name,)).fetchone()
        else:
            data = self.cur.execute("SELECT `id`,`name`,`points`,`permission` FROM `user` WHERE `id`=?",
                (uid,)).fetchone()
        if data==None:
            return False
        user.userId = data[0]
        user.userName = data[1]
        user.points = data[2]
        user.permission = data[3]
        return True

    def getUserIdByName(self, name):
        data = self.cur.execute("SELECT `id` FROM `user` WHERE `name`=?",(name,)).fetchone()
        if data==None:
            return None
        return data[0]

    def didUserSendLink(self, uid):
        data = self.cur.execute("SELECT `sentLink` FROM `user` WHERE `id`=?",(uid,)).fetchone()
        if data==None:
            return False
        return data[0]==1

    def setUserSentLink(self, uid, val):
        deta = self.cur.execute("UPDATE `user` SET `sentLink`=? WHERE `id`=?",(1 if val else 0, uid,))
        self.conn.commit()

    def getNumNotifsForUser(self, uid):
        if globalVals.userNotifCache.isCacheValid(uid):
            return globalVals.userNotifCache.getCache(uid)
        data = self.cur.execute("SELECT `numNots`,`points` FROM `user` WHERE `id`=?",(uid,)).fetchone()
        data = (data[0],data[1])
        globalVals.userNotifCache.cache(uid, data)
        return data

    def clearNotifsForUser(self, uid):
        data = self.cur.execute("UPDATE `user` SET `numNots`=0 WHERE `id`=?",(uid,)).fetchone()
        self.conn.commit()
        globalVals.userNotifCache.invalidateCache(uid)

    def getPostsByRating(self, page):
        pageSize = 20
        if globalVals.postCache.isCacheValid(page):
            return globalVals.postCache.getCache(page)

        data = self.cur.execute("SELECT * FROM `post` ORDER BY `points` DESC LIMIT ? OFFSET ?",
            (pageSize, pageSize*(page-1),)).fetchall()
        posts = map(self.mapCols, data)

        globalVals.postCache.cache(page, posts)
        return posts

    def getPostById(self, pid):
        data = self.cur.execute("SELECT * FROM `post` WHERE `id`=?",(pid,)).fetchone()
        if data==None:
            return None
        return self.mapCols(data)

    def addPost(self, user, title, body, permission=0, raw=False):
        error = 0
        if len(title) > 300:
            title = title[:300]
            error = 1
        if len(body) > 40000:
            body = body[:40000]
            error |= 2
        self.cur.execute("INSERT INTO `post` (`user`, `userName`, `title`, `body`, `time`,`permission`,`raw`) VALUES (?,?,?,?,?,?,?)",
            (user.userId, user.userName, title, body, int(time.time()),permission,1 if raw else 0,))
        self.conn.commit()
        globalVals.postCache.invalidateCache()
        return self.cur.lastrowid

    def getCommentsByRating(self, post):
        if globalVals.commentCache.isCacheValid(post):
            return globalVals.commentCache.getCache(post)

        data = self.cur.execute("SELECT * FROM `comment` WHERE `post`=? ORDER BY `points` DESC",
            (post,)).fetchall()
        comments = map(self.mapCols, data)

        globalVals.commentCache.cache(post, comments)
        return comments

    def addComment(self, user, post, body):
        postTest = self.cur.execute("SELECT `id` FROM `post` WHERE `id`=?",(post,)).fetchone()
        if postTest==None:
            return False
        self.cur.execute("INSERT INTO `comment` (`user`,`userName`,`post`,`body`,`time`) VALUES (?,?,?,?,?)",
            (user.userId, user.userName, post, body, int(time.time())))
        self.cur.execute("UPDATE `post` SET `numComments`=`numComments`+1 WHERE `id`=?",(post,))

        self.conn.commit()

        globalVals.commentCache.invalidateCache(post)
        globalVals.postCache.invalidateCache()
        return True

    def getVote(self, user, post=None, comment=None):
        if not user.loggedIn:
            return 0
        if comment==None:
            vote = self.cur.execute("SELECT `way` FROM  `vote` WHERE `user`=? AND `post`=?",
                (user.userId, post)).fetchone()
        else:
            vote = self.cur.execute("SELECT `way` FROM  `vote` WHERE `user`=? AND `comment`=?",
                (user.userId, comment)).fetchone()
        if vote==None:
            return 0
        return vote[0]

    def addVote(self, user, way, cv, post=None, comment=None):
        if cv<0 and way>0:
            chg = 2
        elif cv>0 and way<0:
            chg = -2
        else:
            chg = -1 if way-cv<0 else 1
        if comment==None:
            postTest = self.cur.execute("SELECT `points`,`user` FROM `post` WHERE `id`=?",(post,)).fetchone()
            if postTest==None:
                return False

            if cv==0:
                self.cur.execute("INSERT INTO `vote` (`user`,`post`,`way`) VALUES (?,?,?)",
                    (user.userId, post, way))
            elif way==0:
                self.cur.execute("DELETE FROM `vote` WHERE `user`=? AND `post`=?", (user.userId, post))
            else:
                self.cur.execute("UPDATE `vote` SET `way`=? WHERE `post`=? AND `user`=?",(way, post, user.userId))
            self.cur.execute("UPDATE `post` SET `points`=? WHERE `id`=?",(postTest[0]+chg,post,))
            self.cur.execute("UPDATE `user` SET `points`=`points`+? WHERE `id`=?",(chg,postTest[1]))
            self.conn.commit()
            globalVals.userNotifCache.invalidateCache(postTest[1])
            globalVals.postCache.invalidateCache()
        else:
            postTest = self.cur.execute("SELECT `points`,`user` FROM `comment` WHERE `id`=?",(comment,)).fetchone()
            if postTest==None:
                return False

            if cv==0:
                self.cur.execute("INSERT INTO `vote` (`user`,`comment`,`way`) VALUES (?,?,?)",
                    (user.userId, comment, way))
            elif way==0:
                self.cur.execute("DELETE FROM `vote` WHERE `user`=? AND `comment`=?", (user.userId, comment))
            else:
                self.cur.execute("UPDATE `vote` SET `way`=? WHERE `comment`=? AND `user`=?", (way, comment, user.userId))
            self.cur.execute("UPDATE `comment` SET `points`=? WHERE `id`=?",(postTest[0]+chg,comment,))
            self.cur.execute("UPDATE `user` SET `points`=`points`+? WHERE `id`=?",(chg,postTest[1]))
            self.conn.commit()
            globalVals.userNotifCache.invalidateCache(postTest[1])
            globalVals.commentCache.invalidateCache(post)
        return True

    def sendMessage(self, user, to, body, raw=False):
        cu = self.cur.execute("SELECT `numNots` FROM `user` WHERE `id`=?",(to,)).fetchone()
        if cu==None:
            return False
        self.cur.execute("INSERT INTO `message` (`to`,`from`,`fromName`,`body`,`time`,`raw`) VALUES (?,?,?,?,?,?)",
            (to, user.userId, user.userName, body, int(time.time()), 1 if raw else 0 ))
        self.cur.execute("UPDATE `user` SET `numNots`=? WHERE `id`=?",(cu[0]+1,to,))
        self.conn.commit()
        globalVals.userNotifCache.invalidateCache(to)
        globalVals.messageCache.invalidateCache(to)
        return True

    def getMessages(self, user):
        if globalVals.messageCache.isCacheValid(user.userId):
            return globalVals.messageCache.getCache(user.userId)
        data = self.cur.execute("SELECT * FROM `message` WHERE `to`=? ORDER BY `time` DESC",
            (user.userId,)).fetchall()
        messages = map(self.mapCols, data)

        globalVals.messageCache.cache(user.userId,messages)
        return messages
    
    def getMeme(self):
        data = self.cur.execute("SELECT meme from `user` where `permission`=2").fetchone()
        return data

    def setMeme(self, meme):
        data = self.cur.execute("UPDATE `user` SET meme=? where `permission`=2",(meme,))
