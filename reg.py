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
import jinja2
import os

from google.appengine.ext import ndb
import tusers

from forms import TeamForm
from reginstitution import InstRegForm

from wtforms import Form, BooleanField, TextField, validators

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class RegHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()

		#Get the requested tournament
		tid = self.request.get('t')
		key = ndb.Key('Tournament', int(tid))
		t = key.get()

		reg = t.preRegRecord().get()

		isj = reg.isJudge(user)
		ist = reg.isOpenTeam(user)
		isi = reg.isInstitution(user)

		# Initialise variables so that they can be passed to the view
		iJudges = None
		iTeams = None
		iJudgeCount = 0
		iTeamCount = 0

		# If they are already registered as a team, pre-populate the
		# modify teams form
		if (ist):
			form = TeamForm()
			form.teamName.data = ist.teamName
			form.sp1Name.data = ist.sp1Name
			form.sp2Name.data = ist.sp2Name
			form.sp1Novice.data = ist.sp1Novice
			form.sp2Novice.data = ist.sp2Novice
			form.sp1ESL.data = ist.sp1ESL
			form.sp2ESL.data = ist.sp2ESL

		elif (isi):
			form = InstRegForm()
			form.leadName.data = isi.leadName
			form.phone.data = isi.phone
			iJudges = isi.judges()
			iJudgeCount = iJudges.count(limit=500)
			iTeams = isi.teams()
			iTeamCount = iTeams.count(limit=500)

		else:
			form = None

		template_values = {
			'user' : user,
			't' : t,
			'logout' : tusers.create_logout_url('/'),
			'login' : tusers.create_login_url('/reg?t=' + tid),
			'r' : reg,
			'isj' : isj,
			'ist' : ist,
			'isi' : isi,
			'form' : form,
			'regd' : (isj!=None) or (ist!=None) or (isi!=None),
			'iTeams' : iTeams,
			'iJudges' : iJudges,
			'iJudgeCount' : iJudgeCount,
			'iTeamCount' : iTeamCount
		}
		template = JINJA_ENVIRONMENT.get_template('view/reg.html')
		self.response.write(template.render(template_values))



app = webapp2.WSGIApplication([
	('/reg', RegHandler)
], debug=True)
