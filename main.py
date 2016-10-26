#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        gastros = Gastro.query().fetch()
        params = {"gastros": gastros}
        return self.render_template("hello.html", params=params)

class InputHandler(BaseHandler): #reading the input information
    def get(self):
        return self.render_template("input.html")

    def post(self):
        rename = self.request.get("name")  #name of the Restaurant
        restreet = self.request.get("street") #street of the Restaurant
        replz = self.request.get("plz") #post code of the Restaurant
        replace = self.request.get("ort") #town/city of the Restaurant
        reinfo = self.request.get("info") #Note Text of the Restaurant
        revisit = self.request.get("visit") #Visit time of the Restaurant
        price = int(self.request.get("price")) #Price Info of the Restaurant
        rating = int(self.request.get("rating")) #Self Rating of the Restaurant
        rekitchen = self.request.get("kueche") #what for kitchen gives in the Restaurant

        lokal = Gastro(lokal_name = rename, lokal_street = restreet, lokal_plz = replz, lokal_place = replace, lokal_note = reinfo, lokal_time = revisit, lokal_kitchen = rekitchen, lokal_rating = rating, lokal_price = price)
        lokal.put()
        gastros = Gastro.query().fetch()
        params = {"gastros": gastros}
        return self.render_template("hello.html", params=params)

class Gastro(ndb.Model):
    lokal_name = ndb.StringProperty()
    lokal_street = ndb.StringProperty()
    lokal_plz = ndb.StringProperty()
    lokal_place = ndb.StringProperty()
    lokal_note = ndb.StringProperty()
    lokal_time = ndb.StringProperty()
    lokal_kitchen = ndb.StringProperty()
    lokal_price = ndb.IntegerProperty()
    lokal_rating = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class ReviewHandler(BaseHandler):
    def get(self, reviews_id):
        reviews = Gastro.get_by_id(int(reviews_id))
        params ={"reviews": reviews}
        return self.render_template("review.html", params=params)

    def post(self, reviews_id):
        #new_user = self.request.get("newuser")
        new_review = self.request.get("newreview")
        new_price = int(self.request.get("newprice"))
        new_rating = int(self.request.get("newrating"))
        new_visit = self.request.get("newvisit")

        reviews = Gastro.get_by_id(int(reviews_id))
        reviews.lokal_note = new_review
        reviews.lokal_price = new_price
        reviews.lokal_rating = new_rating
        reviews.lokal_visit = new_visit
        reviews.put()
        redetail = Gastro.get_by_id(int(redetail_id))
        params = {"redetail": redetail}
        return self.render_template("detail.html", params=params)


class Review(ndb.Model):
    review_user = ndb.StringProperty()
    review_note = ndb.StringProperty()
    review_price = ndb.StringProperty()
    review_rating = ndb.StringProperty()
    review_visit = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class DetailHandler(BaseHandler):
    def get(self, redetail_id):
        redetail = Gastro.get_by_id(int(redetail_id))
        params = {"redetail": redetail}
        return self.render_template("rest_details.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/input.html', InputHandler),
    webapp2.Route('/restaurant/<reviews_id:\d+>/review', ReviewHandler),
    webapp2.Route('/restaurant/<redetail_id:\d+>/details', DetailHandler, name="review-list"),
], debug=True)
