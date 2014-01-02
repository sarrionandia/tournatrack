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
import logging
import datetime
import string
import random

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

from models import Tournament
from models import OwnerInvitation

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def pin_gen(size=35, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))


class InvitationHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#Get the requested tournament
		tid = self.request.get('t')
		t_key = ndb.Key('Tournament', int(tid))
		t = t_key.get()
				
		if (user and user in t.owner):
			#Get all of the invitations whose parent is the current tournament
			q = t.invitations()
			
			template_values = {
				'user' : user,
				't' : t,
				'invitations' : q,
			}
			template = JINJA_ENVIRONMENT.get_template('view/invitations.html')
			self.response.write(template.render(template_values))
						
		else:
			self.redirect(users.create_login_url(self.request.uri))
	
	def post(self):
		user = users.get_current_user()
		
		#Get the requested tournament
		tid = self.request.get('t')
		t_key = ndb.Key('Tournament', int(tid))
		t = t_key.get()
				
		if (user and user in t.owner):
			#Create a new Invitation object whose parent is the tournament
			invitation = OwnerInvitation(parent=t_key)
			invitation.email = self.request.get('email')
			invitation.invited = datetime.datetime.now()
			invitation.pin = pin_gen()
			invitation.put()
			
			#Email them
			url = "http://tournatrack.appspot.com/accept_invitation?t=" + str(t_key.id()) + "&p=" + invitation.pin
			mail.send_mail(sender="Tournatrack <no-reply@tournatrack.appspotmail.com>",
			              to="<"+invitation.email+">",
			              subject="Invitation to manage " + t.name,
			              body= url)
			
			
			#Redirect to the invite page
			self.redirect('/invitations?t=' + str(t_key.id()))
		else:
			self.redirect(users.create_login_url(self.request.uri))
		


app = webapp2.WSGIApplication([
	('/invitations', InvitationHandler)
], debug=True)
