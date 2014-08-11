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
import string
import random
import datetime

from google.appengine.ext import ndb
import tusers

from models import Tournament, Attending

from forms import ProfileForm

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class UpdateProfileHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:

      name = user.full_name
      current_institution = user.current_institution
      public = user.public_profile
      phone = user.phone

      form = ProfileForm()
      form.name.data = name
      form.institution.data = current_institution
      form.public.data = public
      form.phone.data = phone

      template_values = {
        'user' : user,
        'logout' : tusers.create_logout_url('/'),
        'form' : form
      }
      template = JINJA_ENVIRONMENT.get_template('view/update_profile.html')
      self.response.write(template.render(template_values))

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

  def post(self):
    user = tusers.get_current_user()

    if user:

      form = ProfileForm(self.request.POST)
      if (form.validate()):
        user.full_name = form.name.data
        user.current_institution = form.institution.data
        user.public_profile = form.public.data
        user.phone = form.phone.data
        user.put()

        if form.email.data:
          user.change_email(form.email.data)

        if form.email_code.data:
          user.verify_email(form.email_code.data)

        self.redirect('/update_profile')

      else:

        template_values = {
          'user' : user,
          'logout' : tusers.create_logout_url('/'),
          'form' : form
        }
        template = JINJA_ENVIRONMENT.get_template('view/update_profile.html')
        self.response.write(template.render(template_values))

    else:
      self.redirect(tusers.create_login_url(self.request.uri))

class ClearEmailHandler(webapp2.RequestHandler):
  def get(self):
    user = tusers.get_current_user()

    if user:
      user.custom_email = None
      user.email_verified = False
      user.put()
      self.redirect('/update_profile')

    else:
      self.redirect(tusers.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([
  ('/update_profile', UpdateProfileHandler),
  ('/update_profile/clear_email', ClearEmailHandler)
], debug=True)
