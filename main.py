import webapp2
import json
import datetime
import logging
import jinja2
import os
from time import sleep

from google.appengine.ext import ndb
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class GetLoginUrlHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.redirect(users.create_login_url('/home'))


def send_json(request_handler, props):
    request_handler.response.content_type = 'application/json'
    request_handler.response.out.write(json.dumps(props))

class GetUserHandler(webapp2.RequestHandler):
    def dispatch(self):
        email = get_current_user_email()
        result = {}
        if email:
            result['user'] = email
        else:
            result['error'] = 'User is not logged in.'
        print(Log.query().fetch())

class GetAboutPage(webapp2.RequestHandler):
    def dispatch(self):
        email = get_current_user_email()
        template = JINJA_ENVIRONMENT.get_template('templates/about.html')
        self.response.write(template.render(email=email))


class GetHomePageHandler(webapp2.RequestHandler):
    def get(self):
        email = get_current_user_email()
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(email=email, add=False))


class GetAddPageHandler(webapp2.RequestHandler):
    def get(self):
        email = get_current_user_email()
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(email=email, add=True))


def get_current_user_email():
    current_user = users.get_current_user()
    if current_user:
        return current_user.email()
    else:
        return None

def get_current_user_distance():
    current_distance = users.get_current_distance()
    if current_distance:
        return current_user.distance()
    else:
        return None

def get_current_user_transportation():
    current_transportation = users.get_current_transportation()
    if current_transportation:
        return current_user.transportation()
    else:
        return None


class GetLogoutUrlHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.redirect(users.create_logout_url('/home'))


class LogDataHandler(webapp2.RequestHandler):
    def post(self):
        email = get_current_user_email()
        print email
        if email:
            mpg = float(self.request.get('mpg'))
            distance = float(self.request.get('distance'))
            transportation = self.request.get('way')
            comment = self.request.get('comment')
            co2 = round(20.00 / mpg * distance, 2)
            cost = round(float(self.request.get('cost')) * (distance / mpg), 2)
            if transportation == "running":
                calories = distance * 100
            elif transportation == "walking":
                calories = distance * 75
            elif transportation == "biking":
                calories = distance * 40
            else:
                calories = 0
            #print co2
            log = Log(email=email, comment=comment, transportation=transportation, cost= cost, co2=co2, calories=calories, distance=distance, timestamp=str(datetime.datetime.now()))
            #print log
            log.put()
            sleep(.5)
            self.redirect('/report')
        else:
            self.redirect('/login')


class ViewReportHandler(webapp2.RequestHandler):
    def get(self):
        email = get_current_user_email()
        if email:
            q = Log.query().filter(Log.email == email).order(-Log.timestamp)
            log = q.get()
            if log:
                params = {'transportation': log.transportation, 'comment': log.comment, 'timestamp': log.timestamp, 'distance': log.distance,'calories': log.calories, 'cost': log.cost, 'co2': log.co2, 'email': email}
                template = JINJA_ENVIRONMENT.get_template('templates/report.html')
                self.response.write(template.render(params))
            else:
                # redirect to the data form
                self.redirect("/add")
                print 'redirect to the data form'
                pass
        else:
            print "redirect to login"
            pass


class ViewHistoryHandler(webapp2.RequestHandler):
    def get(self):
        email = get_current_user_email()
        if email:
            q = Log.query().filter(Log.email == email).order(-Log.timestamp)
            total_distance = 0
            total_co2 = 0
            total_savings = 0
            total_calories = 0
            for item in q:
                total_distance += item.distance
                total_co2 += item.co2
                total_savings += item.cost
                total_calories += item.calories
            template = JINJA_ENVIRONMENT.get_template('templates/history.html')
            self.response.write(template.render(history=q, email=email, total_distance=total_distance, total_savings=total_savings, total_co2=total_co2, total_calories=total_calories))
        else:
            print "hi"
    #add in other attributes of the Log class
class Comment(ndb.Model):
    email = ndb.StringProperty(required=True)
    text = ndb.StringProperty(required=True)
    timestamp = ndb.StringProperty(required=True)
    logId = ndb.StringProperty(required=True)

class Log(ndb.Model):
    email = ndb.StringProperty(required=True)
    distance = ndb.FloatProperty(required=True)
    timestamp = ndb.StringProperty(required=True)
    transportation = ndb.StringProperty(required=True)
    co2 = ndb.FloatProperty(required=True)
    calories = ndb.FloatProperty(required=True)
    comment = ndb.StringProperty(required=True)
    #user_comments = ndb.KeyProperty(
      #Comment, repeated=True)
    cost = ndb.FloatProperty(required=True)

class ViewFeedHandler(webapp2.RequestHandler):
    def get(self):
        email = get_current_user_email()
        if email:
            q1 = Comment.query().order(-Log.timestamp).fetch()
            log=q1
            for comments in q1:
                if log:
                    # params = {'Email': comments.email, 'Text': comments.text, 'timestamp': comments.timestamp, 'Comment':shsjfhhsjdfj.comment}
                    template = JINJA_ENVIRONMENT.get_template('templates/chat.html')
                    # self.response.write(comments.text)
                    # print comments.key.id()
            q = Log.query().order(-Log.timestamp).fetch(10)
            # for item in q:
            #     self.response.write("<br>")
            #     self.response.write(item)
            template = JINJA_ENVIRONMENT.get_template('templates/chat.html')
            self.response.write(template.render(feed=q, email=email, comments=q1))
    def post(self):
        email = get_current_user_email()
        if email:
            text = str(self.request.get('text'))
            logId = self.request.get("logId")
            #log = Log.get_by_id(logId)
            #log = q.get()
            comment = Comment(email=email, text=text, timestamp=str(datetime.datetime.now()), logId=logId)
            comment.put()
            #log.user_comments.append(comment.key)
            #self.response.write(comment.email +" said "+ comment.text)
        sleep(.5)
        self.redirect("/feed")

    def to_dict(self):
        log = {
                'user': self.email,
                'distance': self.distance,
                'timestamp': self.timestamp.strftime('%Y-%m-%d %I:%M:%S'),
                'transportation': self.transportation,
                'co2': self.co2,
                'calories': self.calories,
                'comment': self.comment,
                'cost': self.cost
            }
        return log

# class CommentDataHandler(webapp2.RequestHandler):
#     def dispatch(self):
#         email = get_current_user_email()
#         if email:
#             text = str(self.request.get('text'))
#             logId = self.request.get("logId")
#             comment = Comment(email=email, text=text, timestamp=str(datetime.datetime.now()), logId=logId)
#             comment.put()

app = webapp2.WSGIApplication([
	('/', GetUserHandler),
	('/home', GetHomePageHandler),
    ('/about', GetAboutPage),
    ('/add', GetAddPageHandler),
	('/user', GetUserHandler),
	('/login', GetLoginUrlHandler),
	('/logout', GetLogoutUrlHandler),
	('/data', LogDataHandler),
	('/report', ViewReportHandler), #view your most recent accomplishment
	('/history', ViewHistoryHandler), #views all the progress
    ('/feed', ViewFeedHandler), #how do you add separate comment threads to each post
    #('/comment', CommentDataHandler)
], debug=True)
