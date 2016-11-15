import json
import requests
# Tests for the validator

# Helper functions

def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))

# returns submission ID
def insert_sub(server, sub_description):
    r = requests.post(url_for(server, "submissions"),
                      json={"description": sub_description})
    submission = json.loads(r.text)["submission"]
    return submission["id"]

def delete_sub(server, sub_id):
    r = requests.delete(url_for(server, "submissions/{}".format(sub_id)))

# Takes ID, returns the result json
def validate_sub(server, sub_id):
    r = requests.get(url_for(server, "validate/{}".format(sub_id)))
    return json.loads(r.text)


# Tests
def test_validator(server):

  # A receipt must be nonempty
  sub_id = insert_sub(server, "")
  res = validate_sub(server, sub_id)
  assert(res['validated'] == False)

  # A receipt must have at least one data line
  sub_id = insert_sub(server, "program\tproject\tcenter\tsubmitter")
  res = validate_sub(server, sub_id)
  assert(res['validated'] == False)

  # A receipt must not have extra or missing data columns 
  sub_id = insert_sub(server, "program\tproject\tcenter\tsubmitter\nTEST\nTEST")
  res = validate_sub(server, sub_id)
  assert(res['validated'] == False)

