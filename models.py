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
import logging

class Tournament(ndb.Model):
	"""Models an individual tournament"""
	name = ndb.StringProperty()
	owner = ndb.UserProperty(repeated=True)
	trackpin = ndb.StringProperty()
	
	def institutions(self):
		return Institution.query(ancestor=self.key).order(Institution.name)
		
	def rooms(self):
		return Room.query(ancestor=self.key).order(Room.name)
		
	def invitations(self):
		return OwnerInvitation.query(ancestor=self.key)
		
	def destroy(self):
		for i in self.institutions():
			i.key.delete()
		for r in self.rooms():
			r.key.delete()
		self.key.delete()

class OwnerInvitation(ndb.Model):
	"""Models an invitation to become a tournament owner"""
	email = ndb.StringProperty();
	pin = ndb.StringProperty();
	invited = ndb.DateTimeProperty();
	
class Institution(ndb.Model):
	"""Models an institution"""
	name = ndb.StringProperty()
	
class Room(ndb.Model):
	"""Models a room in a tournament"""
	name = ndb.StringProperty()
	active = ndb.BooleanProperty()
	status = ndb.StringProperty()
	changed = ndb.TimeProperty()
	comment = ndb.StringProperty()
	