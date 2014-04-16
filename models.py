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

	#Return a list of rooms attached to the tournament
	def rooms(self):
		return Room.query(ancestor=self.key).order(Room.name)

	#Return the pre-registration record for the tournament
	def preRegRecord(self):
		return PreRegRecord.query(ancestor=self.key)

	#Delete the tournament and its attached rooms and registration record
	def destroy(self):
		for r in self.rooms():
			r.key.delete()
		self.preRegRecord().destroy()
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

	#Delete the object and its associated judges, teams, and institutions
	def destroy(self):
		for j in self.indyJudges():
			j.key.delete()
		for t in self.teams():
			t.key.delete()
		for i in self.institutions():
			i.destroy()
		self.key.delete()

	def isRegistered(self, tuser):
		if tuser:
			return self.isInstitution(tuser) or self.isJudge(tuser) or self.isOpenTeam(tuser)


	#Independent Judges registered
	def indyJudges(self):
		return RegisteredIndependentJudge.query(ancestor=self.key)

	#Check if a user is registered as a judge
	def isJudge(self, tuser):
		if tuser:
			q = RegisteredIndependentJudge.query(ancestor=self.key)
			q = q.filter(RegisteredIndependentJudge.user == tuser.key)

			return q.get()
		else:
			return None

	#Check if a user is registered a an Open Team
	def isOpenTeam(self, tuser):
		if tuser:
			q = RegisteredOpenTeam.query(ancestor=self.key)
			q = q.filter(RegisteredOpenTeam.user == tuser.key)

			return q.get()
		else:
			return None

	#Check if a user is registered as an institution
	def isInstitution(self, tuser):
		if tuser:
			q = RegisteredInstitution.query(ancestor=self.key)
			q = q.filter(RegisteredInstitution.user == tuser.key)

			return q.get()
		else:
			return None

	#Teams registered
	def teams(self):
		return RegisteredOpenTeam.query(ancestor=self.key)

	#Institutions registered
	def institutions(self):
		return RegisteredInstitution.query(ancestor=self.key)

	#Return the total number of teams, independent + institutional
	def totalTeamCount(self):
		nTeams = self.teams().count(limit=1000)
		for i in self.institutions():
			nTeams = nTeams + i.teams().count(limit=1000)
		return nTeams

	#Return the total number of judges, independent + institutional
	def totalJudgeCount(self):
		nJudges = self.indyJudges().count(limit=1000)
		for i in self.institutions():
			nJudges = nJudges + i.judges().count(limit=1000)
		return nJudges

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


class RegisteredInstitution(ndb.Model):
	"""Models an institution registered for the tournment"""
	name = ndb.StringProperty()
	leadName = ndb.StringProperty()
	phone = ndb.StringProperty()
	user = ndb.KeyProperty(kind='TUser')
	email = ndb.StringProperty()

	#Return a query of all of the teams attached to the institution
	def teams(self):
		return InstitutionTeam.query(ancestor=self.key)

	#Return a query of all of the judges attached to the institution
	def judges(self):
		return InstitutionJudge.query(ancestor=self.key)

	#Delete the institution along with its teams and judges
	def destroy(self):
		for judge in self.judges():
			judge.key.delete()
		for team in self.teams():
			team.key.delete()
		self.key.delete()


class InstitutionTeam(ndb.Model):
	"""A team attached to an institution"""
	teamName = ndb.StringProperty()
	sp1Name = ndb.StringProperty()
	sp2Name = ndb.StringProperty()
	sp1ESL = ndb.BooleanProperty()
	sp2ESL = ndb.BooleanProperty()
	sp1Novice = ndb.BooleanProperty()
	sp2Novice = ndb.BooleanProperty()


class InstitutionJudge(ndb.Model):
	"""A judge attached to an institution"""
	name = ndb.StringProperty()
	cv = ndb.TextProperty()


class RegisteredPreferences(ndb.Model):
	"""The preferences of a registered participant"""
	vegetarian = ndb.BooleanProperty()
	glutenfree = ndb.BooleanProperty()
	vegan = ndb.BooleanProperty()
	halal = ndb.BooleanProperty()
	kosher = ndb.BooleanProperty()
	special = ndb.StringProperty()
		
	