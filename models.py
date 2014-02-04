# Copyright 2014 Roberto Brian Sarrionandia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.ext import ndb
import logging

class TUser(ndb.Model):
	"""Models a user account"""
	g_user = ndb.UserProperty()
	nickname = ndb.StringProperty()

class Tournament(ndb.Model):
	"""Models an individual tournament"""
	name = ndb.StringProperty()
	owner = ndb.KeyProperty(kind='TUser', repeated=True)
	trackpin = ndb.StringProperty()
	start = ndb.DateProperty()
	end = ndb.DateProperty()
			
	def rooms(self):
		return Room.query(ancestor=self.key).order(Room.name)
		
	def invitations(self):
		return OwnerInvitation.query(ancestor=self.key)
	
	def preRegRecord(self):
		return PreRegRecord.query(ancestor=self.key)
		
	def destroy(self):
		for i in self.institutions():
			i.key.delete()
		for r in self.rooms():
			r.key.delete()
		self.key.delete()

class Room(ndb.Model):
	"""Models a room in a tournament"""
	name = ndb.StringProperty()
	active = ndb.BooleanProperty()
	status = ndb.StringProperty()
	changed = ndb.TimeProperty()
	comment = ndb.StringProperty()
	
class PreRegRecord(ndb.Model):
	"""Models the pre-registration of a tournament"""
	open = ndb.BooleanProperty()
	teamCap = ndb.IntegerProperty()	
	
	def indyJudges(self):
		return RegisteredIndependentJudge.query(ancestor=self.key)
		
	def isJudge(self, tuser):
		if tuser:
			q = RegisteredIndependentJudge.query(ancestor=self.key)
			q = q.filter(RegisteredIndependentJudge.user == tuser.key)
		
			return q.get()
		else:
			return None
	
	def isOpenTeam(self, tuser):
		if tuser:
			q = RegisteredOpenTeam.query(ancestor=self.key)
			q = q.filter(RegisteredOpenTeam.user == tuser.key)
			
			return q.get()
		else:
			return None
	def teams(self):
		return RegisteredOpenTeam.query(ancestor=self.key)
	
class RegisteredIndependentJudge(ndb.Model):
	"""Models a participant in the tournament"""
	name = ndb.StringProperty()
	cv = ndb.TextProperty()
	email = ndb.StringProperty()
	phone = ndb.StringProperty()
	user = ndb.KeyProperty(kind='TUser')
	
	def prefs(self):
		return RegisteredPreferences.query(ancestor=self.key).get()
	
class RegisteredOpenTeam(ndb.Model):
	"""Models an open team in the tournament"""
	leadName = ndb.StringProperty()
	email = ndb.StringProperty()
	phone = ndb.StringProperty()
	user = ndb.KeyProperty(kind='TUser')
	teamName = ndb.StringProperty()
	sp1Name = ndb.StringProperty()
	sp2Name = ndb.StringProperty()
	sp1ESL = ndb.BooleanProperty()
	sp2ESL = ndb.BooleanProperty()
	sp1Novice = ndb.BooleanProperty()
	sp2Novice = ndb.BooleanProperty()

class RegisteredPreferences(ndb.Model):
	"""The preferences of a registered participant"""
	vegetarian = ndb.BooleanProperty()
	glutenfree = ndb.BooleanProperty()
	vegan = ndb.BooleanProperty()
	halal = ndb.BooleanProperty()
	kosher = ndb.BooleanProperty()
	special = ndb.StringProperty()
		
	