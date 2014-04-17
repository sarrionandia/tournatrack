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
	def get(self):
		user = tusers.get_current_user()
		tid = self.request.get('t')

		if not user:
			self.redirect('/reg?t=' + tid)
		
		#Get the requested tournament
		key = ndb.Key('Tournament', int(tid))
		t = key.get()
			
		reg = t.preRegRecord().get()
		
		isi = reg.isInstitution(user)
		
		#Check if they are registered as an institution
		if isi:
			jid = self.request.get('j')
			j_key = ndb.Key('InstitutionJudge', int(jid), parent=isi.key)
			j = j_key.get()
			j_key.delete()
			self.redirect(self.request.referer)
			
		else:
			self.redirect('/reg?t=' + tid)


app = webapp2.WSGIApplication([
	('/dereg_i_judge', DeregHandler)
], debug=True)
