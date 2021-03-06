#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import json
import urllib
from google.appengine.api import urlfetch
from google.appengine.api import users

from base import BaseHandler
from model import Gastro, Recommendation, Review

######################################################################################################################
# Main System with Input and Detail Handler
######################################################################################################################

##########################################
#First page                             ##
##########################################

class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logged_in = True #is user Login
            nickname = user.nickname() #user name
            logout_url = users.create_logout_url('/') #url for logout
            gastros = Gastro.query().fetch() #handing over of the restaurant list
            params = {"logged_in": logged_in, "nickname": nickname, "logout_url": logout_url, "user": user, "gastros":gastros} #handing over all information for rendering the webpage

        else:
            logged_in = False #is user Login
            login_url = users.create_login_url('/') #url for login
            params = {"logged_in": logged_in, "login_url": login_url, "user": user} #handing over all information for rendering the login page

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

        lokal = Gastro(user = user.email(), name = rename, street = restreet, plz = replz, place = replace, note = reinfo, time = revisit, kitchen = rekitchen, rating = rating, price = price)
        lokal.put()
        return self.redirect_to("rest-list")

################################################################################################################
#Restaurant Detail Handler
################################################################################################################

class DetailHandler(BaseHandler):
    def get(self, redetail_id):
        redetail = Gastro.get_by_id(int(redetail_id))


        q = urllib.urlencode({
            "query": (redetail.name + " in " + redetail.place).encode(encoding='ascii', errors='ignore'),
            "key": "AIzaSyBKdIPR1Q6TzIvjJuJzIyvybo6Mg1JLm64"
        })

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + q
        result = urlfetch.fetch(url)

        restaurant_info = json.loads(result.content)

        reviews = Review.query(Review.restaurant == redetail_id).fetch()

        params = {"redetail": redetail, "restaurant_info": restaurant_info, "reviews": reviews}
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

        review = self.request.get("newreview")
        price = int(self.request.get("newprice"))
        rating = int(self.request.get("newrating"))
        visit = self.request.get("newvisit")


        reviews = Review(user = user.email(),note = review, price = price, rating = rating, visit = visit, restaurant = reviews_id)
        reviews.put()
        redetail = Gastro.get_by_id(int(reviews_id))
        q = urllib.urlencode({
            "query": (redetail.name + " in " + redetail.place).encode(encoding='ascii', errors='ignore'),
            "key": "AIzaSyBKdIPR1Q6TzIvjJuJzIyvybo6Mg1JLm64"
        })

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + q
        result = urlfetch.fetch(url)

        restaurant_info = json.loads(result.content)
        params = {"redetail": redetail, "restaurant_info": restaurant_info}
        return self.render_template("rest_details.html", params=params)


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

        recom = Recommendation(user = user.nickname(), name = recname, street = recstreet, plz = recplz, place = recplace, by = recfrom, user_self = recuserself, price = recprice, kitchen = reckitchen)
        recom.put()
        return self.redirect_to("rec-list")


##################################
#Recommendation Detail          ##
##################################
class RecomDetailHandler(BaseHandler):
    def get(self, recoms_id):
        recoms = Recommendation.get_by_id(int(recoms_id))
        q = urllib.urlencode({
            "query": (recoms.name + " in " + recoms.place).encode(encoding='ascii', errors='ignore'),
            "key": "AIzaSyBKdIPR1Q6TzIvjJuJzIyvybo6Mg1JLm64"
        })

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + q
        result = urlfetch.fetch(url)

        restaurant_info = json.loads(result.content)

        params = {"recoms": recoms, "restaurant_info": restaurant_info}
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

        lokal = Gastro(user=user.nickname(), name=rename, street=restreet, plz=replz,
                       place=replace, note=reinfo, time=revisit, kitchen=rekitchen,
                       rating=rating, price=price)
        lokal.put()
        recoms = Recommendation.get_by_id(int(recoms_id))
        recoms.key.delete()
        return self.redirect_to("rest-list")



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
