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

from models import RegisteredIndependentJudge

from forms import JudgeForm

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class JudgeHandler(webapp2.RequestHandler):
	def get(self):
		user = tusers.get_current_user()
		form = JudgeForm()

		j = self.request.get('j')
		j_key = ndb.Key(urlsafe=j)
		judge = j_key.get()

		t = j_key.parent().parent().get()
		reg = t.preRegRecord().get()

		if user.key in t.owner or judge.user == user.key:
			form.name.data = judge.name
			form.phone.data = judge.phone
			form.email.data = judge.email
			form.cv.data = judge.cv

			template_values = {
				'user' : user,
				't' : t,
				'logout' : tusers.create_logout_url('/'),
				'login' : tusers.create_login_url('/mod/judge?j=' + j),
				'r' : reg,
				'form' : form,
				'j' : j_key.urlsafe()
			}
			template = JINJA_ENVIRONMENT.get_template('view/modjudge.html')
			self.response.write(template.render(template_values))
			return
		else:
			self.redirect(self.request.referer)


	def post(self):
		user = tusers.get_current_user()
		form = JudgeForm(self.request.POST)

		j = self.request.get('j')
		j_key = ndb.Key(urlsafe=j)
		judge = j_key.get()

		t = j_key.parent().parent().get()
		reg = t.preRegRecord().get()

		if user.key in t.owner or user.key == judge.user:

			#If valid, create the new judge object
			if (form.validate()):

				judge.name = form.name.data
				judge.phone = form.phone.data
				judge.email = form.email.data
				judge.cv = form.cv.data

				judge.put()

				self.redirect('/reg_control?t=' + str(t.key.id()))
			else:
				template_values = {
					'user' : user,
					't' : t,
					'logout' : tusers.create_logout_url('/'),
					'login' : tusers.create_login_url('/mod/judge?j=' + j),
					'r' : reg,
					'form' : form,
				}
				template = JINJA_ENVIRONMENT.get_template('view/modjudge.html')
				self.response.write(template.render(template_values))
		else:
			self.redirect(self.request.referer)


app = webapp2.WSGIApplication([
	('/mod/judge', JudgeHandler)
], debug=True)
