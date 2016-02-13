import os
import json, urllib
from datetime import datetime

from flask import Flask, jsonify
app = Flask(__name__)

BASEURL = "http://fhir2.healthintersections.com.au/open/"
SEARCHURL = "/_search?_format=text/json&"
SORTURL = "&search-sort=_id"

janegriffinid = 'ad2f3d7c%2D4274%2D4422%2Da10a%2D8e2bc99c40'

@app.route('/patient')
def getPatient(firstname = "Jane", lastname = "Griffin"):
# Request: http://fhir2.healthintersections.com.au/open/Patient/_search?_format=text/json&family=griffin&name=jane&search-sort=_id
	url = BASEURL + "Patient" + SEARCHURL + "family=" + lastname +"&name=" + firstname + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	patient = {}
	patient['First Name'] = firstname
	patient['Last Name'] = lastname
	patient['Birthday'] = data['entry'][0]['resource']['birthDate']
	patient['Gender'] = data['entry'][0]['resource']['gender']

	dateformat = "%Y-%m-%d"
	born = datetime.strptime(patient['Birthday'], dateformat)
	today = datetime.today()
	patient['Age'] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
	patient['Id'] = data['entry'][0]['resource']['id']

	return jsonify(**patient)

@app.route('/allergies')
def getAllergies(id = janegriffinid):
	url = BASEURL + "AllergyIntolerance" + SEARCHURL + "patient._id=" + janegriffinid + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	allergieslist = []
	allergieslist += [data['entry'][0]['resource']['substance']['coding'][0]['display']]
	allergies = {"Allergies":allergieslist}

	return jsonify(**allergies)
#search-id=c6fba785-9c00-4505-b42c-499dd43e8b&&patient._id=ad2f3d7c%2D4274%2D4422%2Da10a%2D8e2bc99c40&search-sort=_id 


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug = True)
