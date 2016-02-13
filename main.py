import os
import json, urllib
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request
app = Flask(__name__)

BASEURL = "http://fhir2.healthintersections.com.au/open/"
JSON = "text/json&"
SEARCH = "/_search?_format="
SEARCHURL = SEARCH + JSON
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
	patient['Age'] = str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))
	patient['Id'] = data['entry'][0]['resource']['id']
	patient['Picture'] = "http://www.deludeddiva.com/wp-content/uploads/2012/09/mean_thumb.jpg"

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


@app.route('/medications')
def getMedications(id = janegriffinid):
	url = BASEURL + "MedicationOrder" + SEARCHURL + "patient._id=" + janegriffinid + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	medicationlist = []
	for meds in data['entry']:
	    medication = {}
	    medication['OrderId'] = meds['resource']['id'] 
	    medication['PatientId'] = meds['resource']['patient']['reference']
	    medication['PractitionerId'] = meds['resource']['prescriber']['reference']
	    medication['EncounterId'] = meds['resource']['encounter']['reference']
	    medication['ConditionId'] = meds['resource']['reasonReference']['reference']
	    medication['PrescriptionCode'] = meds['resource']['medicationCodeableConcept']['coding'][0]['code']
	    medication['PrescriptionDisplay'] = meds['resource']['medicationCodeableConcept']['coding'][0]['display']
	    medicationlist.append(medication)

	medications = {"Medications":medicationlist}
	return jsonify(**medications)

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug = True)
