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

        #Get the requested tournament
        tid = self.request.get('t')
        key = ndb.Key('Tournament', int(tid))
        t = key.get()

        reg = t.preRegRecord().get()
        isi = reg.isInstitution(user)

        logging.info('Adding a new record')

        if isi and reg.open:
            if self.request.get('type') == 't':
                #Register a new Team
                team = InstitutionTeam(parent=isi.key)
                team.put()
                self.redirect('/updateteams?t=' + tid)


            if self.request.get('type') == 'j':
                #Register a new judge
                judge = InstitutionJudge(parent=isi.key)
                judge.put()
                self.redirect('/updatejudges?t=' + tid)

app = webapp2.WSGIApplication([
	('/add_to_reg', RegHandler)
], debug=True)
