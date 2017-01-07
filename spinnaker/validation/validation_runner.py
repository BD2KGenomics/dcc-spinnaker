import sys
import uwsgi
import requests
import json
sys.path.append("/app/spinnaker")
from validation import validation_engine  # noqa: E402


# uWSGI spooler callback function. Runs a validation for
# the submission whose ID is passed in as submission_id.
def spooler(job_info):

    # We will run this on the same server as the main spinnaker app
    server = "http://127.0.0.1:5000"

    print("Spooler callback function is running!")
    print(job_info)
    # Get the submisssion from the ID
    id = job_info['submission_id']

    # connect to the API and get the submission receipt
    r = requests.get("{}/v0/submissions/{}".format(server, id))

    # Check for 404
    if not r.status_code == 200:
        myjson = {"validated": False, "response": "couldn't get submission"}
    else:
        # TODO : verify that submission is in received status - ie ready to validate.
        try:
            receipt = json.loads(r.text)["submission"]["receipt"]
        except KeyError:
            myjson = {"validated": False, "response": "couldn't get receipt", "details": ""}
        else:
            validation_result = validation_engine.run_validations(receipt)
            myjson = {"validated": validation_result.validated,
                      "response": validation_result.response,
                      "details": validation_result.details}

    r = requests.put("{}/v0/validation/{}".format(server, id), json=myjson)
    # TODO : check that r worked

    return uwsgi.SPOOL_OK


uwsgi.spooler = spooler
