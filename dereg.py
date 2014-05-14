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

# This file handles the deregistration of teams, judges, and institutions.

import webapp2

from google.appengine.ext import ndb
import tusers
import logging

from models import Attending

#Handles the deregistration of open teams
class DeregTeamHandler(webapp2.RequestHandler):
	def post(self):
		user = tusers.get_current_user()

		#Check if the t_key parameter is un use
		if self.request.get('t_key', default_value=False):
			key = ndb.Key(urlsafe=self.request.get('t_key'))
			t = key.get()

			if t.authorised(user):
				if key.kind() == 'RegisteredOpenTeam':
					#Remove the attendance record
					q = Attending.query(ancestor=user.key)
					q.filter(Attending.tournament == key.parent().parent())
					q.get(keys_only=True).delete()

				key.delete()
		self.redirect(self.request.referer)

#Handles the deregistration of independent and institutional judges
class DeregJudgeHandler(webapp2.RequestHandler):
	def post(self):
		user = tusers.get_current_user()

		#Check if the j_key parameter is in use.
		if self.request.get('j_key', default_value=False):
			key = ndb.Key(urlsafe=self.request.get('j_key'))
			j = key.get()

			#Delete from the database
			if j.authorised(user):
				if key.kind() == 'RegisteredIndependentJudge':
					#Remove the attendance record
					q = Attending.query(ancestor=user.key)
					q.filter(Attending.tournament == key.parent().parent())
					q.get(keys_only=True).delete()

				key.delete()

		self.redirect(self.request.referer)

class DeregInstitutionHandler(webapp2.RequestHandler):
	def post(self):
		user = tusers.get_current_user()

		#Get the requested tournament
		key = ndb.Key(urlsafe=self.request.get('institution'))
		institution = key.get()

		if institution.authorised(user):
			#Remove the attendance record
			q = Attending.query(ancestor=user.key)
			q.filter(Attending.tournament == key.parent().parent())
			try:
				q.get(keys_only=True).delete()
			except:
				logging.info("No key for attendance record")

			institution.destroy()

		self.redirect(self.request.referer)


app = webapp2.WSGIApplication([
	('/dereg/team', DeregTeamHandler),
	('/dereg/judge', DeregJudgeHandler),
	('/dereg/institution', DeregInstitutionHandler)
], debug=True)
