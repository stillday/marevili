#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
import json
#import simplejson, urllib
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import users


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

################################################################################################################
# Google Place Api Handler
################################################################################################################
GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

def geocode(address, **geo_args):
    geo_args.update({
        'address': address
    })

    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    result = simplejson.load(urllib.urlopen(url))

    print simplejson.dumps([s['formatted_address'] for s in result['results']], indent=2)

if __name__ == '__main__':
    geocode(address="San+Francisco")

######################################################################################################################
# Main System with Input and Detail Handler
######################################################################################################################

##########################################
#First page                             ##
##########################################

class MainHandler(BaseHandler):
    def get(self):
        gastros = Gastro.query().fetch()
        user = users.get_current_user()
        logged_in = user is not None

        params = {"gastros": gastros, "user": user, "logged_in": logged_in}

        if logged_in:
            params["logout_url"] = users.create_logout_url('/')
        else:
            params["login_url"] =  users.create_login_url('/')

        return self.render_template("hello.html", params=params)

##########################################
#Input Handler                          ##
##########################################

class InputHandler(BaseHandler): #reading the input information
    def get(self):
        return self.render_template("input.html")

    def post(self):
        user = users.get_current_user()

        if not user:
            self.render_template("permissiondenied.html" ,params={"login_url": users.create_login_url('/')})
            return


        rename = self.request.get("name")  #name of the Restaurant
        restreet = self.request.get("street") #street of the Restaurant
        replz = self.request.get("plz") #post code of the Restaurant
        replace = self.request.get("ort") #town/city of the Restaurant
        reinfo = self.request.get("info") #Note Text of the Restaurant
        revisit = self.request.get("visit") #Visit time of the Restaurant
        price = int(self.request.get("price")) #Price Info of the Restaurant
        rating = int(self.request.get("rating")) #Self Rating of the Restaurant
        rekitchen = self.request.get("kueche") #what for kitchen gives in the Restaurant

        lokal = Gastro(lokal_user = user.email(), lokal_name = rename, lokal_street = restreet, lokal_plz = replz, lokal_place = replace, lokal_note = reinfo, lokal_time = revisit, lokal_kitchen = rekitchen, lokal_rating = rating, lokal_price = price)
        lokal.put()
        gastros = Gastro.query().fetch()
        user = users.get_current_user()
        logged_in = user is not None
        params = {"gastros": gastros, "user": user, "logged_in": logged_in}
        return self.redirect_to("rest-list", params=params)

class Gastro(ndb.Model): #push in die datenbank
    lokal_user = ndb.StringProperty()
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

################################################################################################################
#Restaurant Detail Handler
################################################################################################################

class DetailHandler(BaseHandler):
    def get(self, redetail_id):
       # url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=seoul+wien&key=AIzaSyBKdIPR1Q6TzIvjJuJzIyvybo6Mg1JLm64"

        #result = urlfetch.fetch(url)

       # restaurant_info = json.loads(result.content)

        redetail = Gastro.get_by_id(int(redetail_id))
        params = {"redetail": redetail}
        return self.render_template("rest_details.html", params=params)


#######################################################################################################################
# Review System
#######################################################################################################################


class ReviewHandler(BaseHandler):
    def get(self, reviews_id):
        reviews = Gastro.get_by_id(int(reviews_id))
        params ={"reviews": reviews}
        return self.render_template("review.html", params=params)

    def post(self, reviews_id):
        user = users.get_current_user()

        if not user:
            self.render_template("permissiondenied.html", params={"login_url": users.create_login_url('/')})
            return
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
        redetail = Gastro.get_by_id(int(reviews_id))
        params = {"redetail": redetail}
        return self.render_template("rest_details.html", params=params)


class Review(ndb.Model):
    review_user = ndb.StringProperty()
    review_note = ndb.StringProperty()
    review_price = ndb.IntegerProperty()
    review_rating = ndb.IntegerProperty()
    review_visit = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


#######################################################################################################################
# Recommendation with input and detail Handler
#######################################################################################################################

##################################
#Recommendation View            ##
##################################

class RecommendationHandler(BaseHandler):
    def get(self):
        recoms = Recommendation.query().fetch()
        params = {"recoms": recoms}
        return self.render_template("recommendation.html", params=params)

##################################
#Recommendation Input           ##
##################################

class RecomInputHandler(BaseHandler):
    def get(self):
        return self.render_template("recom_input.html")

    def post(self):
        user = users.get_current_user() #User Login Information for Database

        if not user:
            self.render_template("permissiondenied.html", params={"login_url": users.create_login_url('/')})
            return

        recname = self.request.get("name") #Restaurant Name
        recstreet = self.request.get("street") #Restaurant Street
        recplz = self.request.get("plz") # Restaurant Zip Code
        recplace = self.request.get("ort") #Restaurant Place
        recfrom = self.request.get("from") #Restaurant Tip from
        recuserself = self.request.get("user") #User Name
        recprice = int(self.request.get("price")) #Price Ranking
        reckitchen = self.request.get("kueche") #what kind of kitchen

        recom = Recommendation(recom_user = user.email(), recom_name = recname, recom_street = recstreet, recom_plz = recplz, recom_place = recplace, recom_from = recfrom, recom_user_self = recuserself, recom_price = recprice, recom_kitchen = reckitchen)
        recom.put()
        recoms = Recommendation.query().fetch()
        params = {"recoms": recoms}
        return self.redirect_to("rec-list", params=params)

class Recommendation(ndb.Model):
    recom_user = ndb.StringProperty()
    recom_name = ndb.StringProperty()
    recom_street = ndb.StringProperty()
    recom_plz = ndb.StringProperty()
    recom_place = ndb.StringProperty()
    recom_from = ndb.StringProperty()
    recom_user_self = ndb.StringProperty()
    recom_price = ndb.IntegerProperty()
    recom_kitchen = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

##################################
#Recommendation Detail          ##
##################################
class RecomDetailHandler(BaseHandler):
    def get(self, recoms_id):
        recoms = Recommendation.get_by_id(int(recoms_id))
        params = {"recoms": recoms}
        return self.render_template("recom_details.html", params=params)

######################################################################################################################
#Recommendation push to Restaurant List
######################################################################################################################

class RecomToRest(BaseHandler):
    def get(self, recoms_id):
        recoms = Recommendation.get_by_id(int(recoms_id))
        params = {"recoms": recoms}
        return self.render_template("recom_push.html", params=params)

    def post(self, recoms_id):
        user = users.get_current_user()

        if not user:
            self.render_template("permissiondenied.html", params={"login_url": users.create_login_url('/')})
            return

        rename = self.request.get("name")  # name of the Restaurant
        restreet = self.request.get("street")  # street of the Restaurant
        replz = self.request.get("plz")  # post code of the Restaurant
        replace = self.request.get("ort")  # town/city of the Restaurant
        reinfo = self.request.get("info")  # Note Text of the Restaurant
        revisit = self.request.get("visit")  # Visit time of the Restaurant
        price = int(self.request.get("price"))  # Price Info of the Restaurant
        rating = int(self.request.get("rating"))  # Self Rating of the Restaurant
        rekitchen = self.request.get("kueche")  # what for kitchen gives in the Restaurant

        lokal = Gastro(lokal_user=user.email(), lokal_name=rename, lokal_street=restreet, lokal_plz=replz,
                       lokal_place=replace, lokal_note=reinfo, lokal_time=revisit, lokal_kitchen=rekitchen,
                       lokal_rating=rating, lokal_price=price)
        lokal.put()
        gastros = Gastro.query().fetch()
        user = users.get_current_user()
        logged_in = user is not None
        params = {"gastros": gastros, "user": user, "logged_in": logged_in}
        recoms = Recommendation.get_by_id(int(recoms_id))
        recoms.key.delete()
        return self.redirect_to("rest-list", params=params)



#######################################################################################################################
# Webapp System
#######################################################################################################################

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="rest-list"),
    webapp2.Route('/input.html', InputHandler),
    webapp2.Route('/recommendation.html', RecommendationHandler, name="rec-list"),
    webapp2.Route('/recom_input.html', RecomInputHandler),
    webapp2.Route('/restaurant/<reviews_id:\d+>/review', ReviewHandler),
    webapp2.Route('/restaurant/<redetail_id:\d+>/details', DetailHandler, name="review-list"),
    webapp2.Route('/recommendation/<recoms_id:\d+>/details', RecomDetailHandler),
    webapp2.Route('/recommendation/<recoms_id:\d+>/visit-input', RecomToRest),
], debug=True)
