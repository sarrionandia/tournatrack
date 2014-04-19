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

from wtforms import Form, TextField, TextAreaField, BooleanField, validators

#Team Form model
class TeamForm(Form):
	leadName = TextField('leadName', [validators.Required()])
	email = TextField('email', [validators.Email()])
	phone = TextField('phone', [validators.Required()])
	teamName = TextField('teamName')
	sp1Name = TextField('sp1Name')
	sp1Novice = BooleanField('sp1Novice')
	sp1ESL = BooleanField('sp1ESL')
	sp2Name = TextField('sp2Name')
	sp2Novice = BooleanField('sp2Novice')
	sp2ESL = BooleanField('sp2ESL')


# Judge Form model
class JudgeForm(Form):
	name = TextField('name', [validators.required()])
	email = TextField('email', [validators.email()])
	phone = TextField('phone', [validators.required()])
	cv = TextAreaField('cv', [validators.optional()])
