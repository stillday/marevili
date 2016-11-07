#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb


class Review(ndb.Model):
    user = ndb.StringProperty()
    note = ndb.StringProperty()
    price = ndb.IntegerProperty()
    rating = ndb.IntegerProperty()
    visit = ndb.StringProperty()
    restaurant = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


class Recommendation(ndb.Model):
    user = ndb.StringProperty()
    name = ndb.StringProperty()
    street = ndb.StringProperty()
    plz = ndb.StringProperty()
    place = ndb.StringProperty()
    by = ndb.StringProperty()
    user_self = ndb.StringProperty()
    price = ndb.IntegerProperty()
    kitchen = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


class Gastro(ndb.Model): #push in die datenbank
    user = ndb.StringProperty()
    name = ndb.StringProperty()
    street = ndb.StringProperty()
    plz = ndb.StringProperty()
    place = ndb.StringProperty()
    note = ndb.StringProperty()
    time = ndb.StringProperty()
    kitchen = ndb.StringProperty()
    price = ndb.IntegerProperty()
    rating = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)