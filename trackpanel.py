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

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Tournament
from models import Room

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class PanelHandler(webapp2.RequestHandler):
	def get(self):
		tid = self.request.get('t')
		t_key = ndb.Key('Tournament', int(tid))
		t = t_key.get()
		user = users.get_current_user()
				
		if (t.trackpin == self.request.get('p')):
			#Check if they want a specific room, or a list of all of the rooms
			if(not self.request.get('r')):
				template_values = {
					't' : t,
					'user' : user,
					'logout' : users.create_logout_url('/'),
					'rooms' : t.rooms(),
					}
				template = JINJA_ENVIRONMENT.get_template('view/alltrackpanels.html')
				self.response.write(template.render(template_values))
				
			else:
				#Get the current room
				rid = self.request.get('r')
				r_key = ndb.Key('Tournament', int(tid), 'Room', int(rid))
				room = r_key.get()
			
				template_values = {
					't' : t,
					'room' : room,
					'user' : user,
					'logout' : users.create_logout_url('/'),
					}
				template = JINJA_ENVIRONMENT.get_template('view/trackpanel.html')
				self.response.write(template.render(template_values))
						
		else:
			self.redirect('/')
	
	def post(self):
		tid = self.request.get('t')
		t_key = ndb.Key('Tournament', int(tid))
		t = t_key.get()
				
		if (t):
			#Get the current room and update the tracking values
			rid = self.request.get('r')
			r_key = ndb.Key('Tournament', int(tid), 'Room', int(rid))
			room = r_key.get()
		
			room.status = self.request.get('status')
			room.comment = self.request.get('comment')
			room.changed = datetime.datetime.now().time()
		
			room.put()
			self.redirect('/trackpanel?t=' + str(t_key.id()) + '&r=' + str(r_key.id()) + '&p=' + t.trackpin)

app = webapp2.WSGIApplication([
	('/trackpanel', PanelHandler)
], debug=True)
