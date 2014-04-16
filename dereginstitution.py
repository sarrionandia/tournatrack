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

class DeregHandler(webapp2.RequestHandler):
	def post(self):
		user = tusers.get_current_user()
		tid = self.request.get('t')
		
		#Get the requested tournament
		institutionkey = self.request.get('institution')
		institution = ndb.Key(urlsafe=institutionkey).get()		
		
		if institution.user == user.key:
			institution.destroy()
		
		self.redirect('/reg?t=' + tid)


app = webapp2.WSGIApplication([
	('/dereg/institution', DeregHandler)
], debug=True)
