from google.appengine.ext import ndb
import logging

class Tournament(ndb.Model):
	"""Models an individual tournament"""
	name = ndb.StringProperty()
	owner = ndb.UserProperty(repeated=True)
	trackpin = ndb.StringProperty()
	
	def institutions(self):
		return Institution.query(ancestor=self.key).order(Institution.name)
		
	def rooms(self):
		return Room.query(ancestor=self.key).order(Room.name)
	
class Institution(ndb.Model):
	"""Models an institution"""
	name = ndb.StringProperty()
	
class Room(ndb.Model):
	"""Models a room in a tournament"""
	name = ndb.StringProperty()
	active = ndb.BooleanProperty()
	