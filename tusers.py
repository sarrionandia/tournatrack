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

# A replacement for the users service to decouple the code from the Google API

from google.appengine.api import users

from models import TUser

def create_logout_url(path):
	return users.create_logout_url(path)
		
def create_login_url(path):
	return users.create_login_url(path)
		
def get_current_user():
	g_ac = users.get_current_user()
	
	#Return none if they aren't signed in to Google
	if (g_ac == None):
		return None
	tu = TUser.query(TUser.g_user==g_ac).get()
	
	#If the user object doesn't exist, create a new one using the currently signed in google account
	if (tu == None):
		tu = TUser()
		tu.g_user = g_ac
		tu.nickname = g_ac.nickname()
		tu.put()
	return tu
		
	