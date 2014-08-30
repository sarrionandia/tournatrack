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
from google.appengine.api import mail

import string
import random

def pin_gen(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))


class TUser(ndb.Model):
	"""Models a user account"""
	g_user = ndb.UserProperty()
	nickname = ndb.StringProperty()
	full_name = ndb.StringProperty()
	current_institution = ndb.StringProperty()
	public_profile = ndb.BooleanProperty()
	custom_email = ndb.StringProperty()
	email_code = ndb.StringProperty()
	email_verified = ndb.BooleanProperty()
	phone = ndb.StringProperty()
	basic_info = ndb.ComputedProperty(lambda self: self.full_name and self.phone)

	def preferredEmail(self):
		if self.email_verified and self.custom_email:
			return self.custom_email
		else:
			return self.g_user.email()

	def change_email(self, email):
		self.email_verified = False
		self.custom_email = email
		self.email_code = pin_gen()
		self.put()

		#Send a verification email
		message = mail.EmailMessage(sender="Tournatrack <noreply@tournatrack.appspotmail.com",
																subject="Verify your email address")
		message.to = self.full_name + ' <' + email + '>'
		message.body = """
		This email address has been added to an account on Tournatrack. We will only
		use it if you take your verification code, and input it to your Account Settings page.

		Your verification code is: %s

		Later!
		-The Tournatrack Lizards
		"""%self.email_code
		message.send()

	def verify_email(self, code):
		if self.email_code == code:
			self.email_verified = True
			self.email_code = None
			self.put()


class Attending(ndb.Model):
	"""Models a user attending a tournament
	The parent of the object will be the TUser attending """
	role = ndb.StringProperty()
	tournament=ndb.KeyProperty(kind='Tournament')

class Tournament(ndb.Model):
	"""Models an individual tournament"""
	name = ndb.StringProperty()
	owner = ndb.KeyProperty(kind='TUser', repeated=True)
	trackpin = ndb.StringProperty()
	start = ndb.DateProperty()
	end = ndb.DateProperty()
	customRoomStatus = ndb.StringProperty(repeated=True)

	#Information to be displayed
	blurb = ndb.TextProperty()
	facebook = ndb.StringProperty()
	homepage = ndb.StringProperty()
	contact_email = ndb.StringProperty()

	#Return the blurb with newlines
	def blurbDisplay(self):
		if self.blurb:
			r = '<br />'
			return self.blurb.replace('\r\n',r).replace('\n\r',r).replace('\r',r).replace('\n',r)
		else:
			return None

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

		preReg = self.preRegRecord().get()
		if preReg:
			preReg.destroy()

		#Get rid of all of the attendance records
		q = Attending.query()
		q.filter(Attending.tournament == self.key)
		keys = q.fetch(keys_only=True)
		ndb.delete_multi(keys)

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
	name = ndb.ComputedProperty(lambda self: self.user.get().full_name)
	phone = ndb.ComputedProperty(lambda self: self.user.get().phone)
	cv_public = ndb.ComputedProperty(lambda self: self.user.get().public_profile)
	user = ndb.KeyProperty(kind='TUser')

	def prefs(self):
		return RegisteredPreferences.query(ancestor=self.key).get()

	#Check if the user is authorised to modify
	def authorised(self, tuser):
		#Check if they own the object
		if self.user == tuser.key:
			return True
		#Check if they own the tournament
		elif tuser.key in self.key.parent().parent().get().owner:
			return True
		else:
			return False

	def email(self):
		return self.user.get().preferredEmail()

class RegisteredOpenTeam(ndb.Model):
	"""Models an open team in the tournament"""
	leadName = ndb.ComputedProperty(lambda self: self.user.get().full_name)
	phone = ndb.ComputedProperty(lambda self: self.user.get().phone)
	user = ndb.KeyProperty(kind='TUser')

	teamName = ndb.StringProperty()

	sp1Key = ndb.KeyProperty(kind='TUser')
	sp2Key = ndb.KeyProperty(kind='TUser')

	sp1Name = ndb.StringProperty()
	sp2Name = ndb.StringProperty()

	sp1ESL = ndb.BooleanProperty()
	sp2ESL = ndb.BooleanProperty()

	sp1Novice = ndb.BooleanProperty()
	sp2Novice = ndb.BooleanProperty()

	def email(self):
		return self.user.get().preferredEmail()

	def authorised(self, tuser):
		if self.user == tuser.key:
			return True
		elif tuser.key in self.key.parent().parent().get().owner:
			return True
		else:
			return False

	def institutionName(self):
		return "Composite"

	#Link a speaker to a registered team
	def linkSpeaker(self, speaker, dID):
		key = ndb.Key('TUser', int(dID))
		debater = key.get()
		if debater.basic_info:
			if speaker == 1:
				self.sp1Key = key
			elif speaker == 2:
				self.sp2Key = key
			else:
				return False
			self.put()
			return True
		else:
			return False

	def linkSpeaker2(self, dID):
		def linkSpeaker1(self, dID):
			key = ndb.Key('TUser', int(dID))
			debater = key.get()
			if debater.basic_info:
				self.sp1Key = key
				return True
			else:
				return False

class RegisteredInstitution(ndb.Model):
	"""Models an institution registered for the tournment"""
	name = ndb.StringProperty()
	leadName = ndb.StringProperty()
	phone = ndb.StringProperty()
	user = ndb.KeyProperty(kind='TUser')

	def email(self):
		return self.user.get().preferredEmail()
	#Return a query of all of the teams attached to the institution
	def teams(self):
		return InstitutionTeam.query(ancestor=self.key)

	#Return a query of all of the judges attached to the institution
	def judges(self):
		return InstitutionJudge.query(ancestor=self.key)

	#Check whether they are authorised to edit
	def authorised(self, tuser):
		return self.user == tuser.key or tuser.key in self.key.parent().parent().get().owner
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

	def authorised(self, tuser):
		return self.key.parent().get().user == tuser.key or  tuser.key in self.key.parent().parent().parent().get().owner

	def institutionName(self):
		return self.key.parent().get().name

class InstitutionJudge(ndb.Model):
	"""A judge attached to an institution"""
	name = ndb.StringProperty()

	#Check if the user is authorised to modify
	def authorised(self, tuser):
		#Check if they own the object
		if self.key.parent().get().user == tuser.key:
			return True
		#Check if they are the tournament owner
		elif tuser.key in self.key.parent().parent().parent().get().owner:
			return True
		else:
			return False


class RegisteredPreferences(ndb.Model):
	"""The preferences of a registered participant"""
	vegetarian = ndb.BooleanProperty()
	glutenfree = ndb.BooleanProperty()
	vegan = ndb.BooleanProperty()
	halal = ndb.BooleanProperty()
	kosher = ndb.BooleanProperty()
	special = ndb.StringProperty()

class PerfSpeakerRecord(ndb.Model):
	"""The performance record of a speaker at a tournament"""
	tournament = ndb.StringProperty()
	startDate = ndb.DateProperty()

	teamRank = ndb.IntegerProperty()
	averageSpeaks = ndb.FloatProperty()
	speakerRank = ndb.IntegerProperty()

	champion = ndb.BooleanProperty()
	finalist = ndb.BooleanProperty()
	semifinalist = ndb.BooleanProperty()
	quarterfinalist = ndb.BooleanProperty()
	octofinalist = ndb.BooleanProperty()
	doubleoctofinalist = ndb.BooleanProperty()

	ESLBreak = ndb.BooleanProperty()
	ESLChampion = ndb.BooleanProperty()
	EFLBreak = ndb.BooleanProperty()
	EFLChampion = ndb.BooleanProperty()

	NoviceBreak = ndb.BooleanProperty()
	NoviceChampion = ndb.BooleanProperty()

	isWin = ndb.BooleanProperty()
	isBreak = ndb.BooleanProperty()

class PerfJudgeRecord(ndb.Model):
	"""The performance record of a judge at a tournament"""
	tournament = ndb.StringProperty()
	startDate = ndb.DateProperty()
	chair = ndb.BooleanProperty()
	broke = ndb.BooleanProperty()
	outroundChair = ndb.BooleanProperty()
	CA = ndb.BooleanProperty()
	DCA = ndb.BooleanProperty()
	equity = ndb.BooleanProperty()
	isAchievement = ndb.BooleanProperty()

	def isCAShip(self):
		response = self.DCA or self.CA
		return response
