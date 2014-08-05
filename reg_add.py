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

import webapp2

from google.appengine.ext import ndb
import tusers

import logging

from models import InstitutionTeam, InstitutionJudge

class RegHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()

		#Get the institution
		i = self.request.get('i')
		i_key = ndb.Key(urlsafe=i)
		institution = i_key.get()

		reg = i_key.parent().get()

		if institution.authorised(user) and reg.open and institution.teams().count(limit=20)<20:
			if self.request.get('type') == 't':
				#Register a new Team
				team = InstitutionTeam(parent=institution.key)
				team.put()

			if self.request.get('type') == 'j':
				#Register a new judge
				judge = InstitutionJudge(parent=institution.key)
				judge.put()

		self.redirect(self.request.referer)

app = webapp2.WSGIApplication([
	('/add_to_reg', RegHandler)
], debug=True)
