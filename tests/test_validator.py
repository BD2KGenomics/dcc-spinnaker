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

# Create a submission, validate it, and delete it.
# Returns whether the validation result was the desired_result
def run_a_validation(server, sub_description, desired_result):
  sub_id = insert_sub(server, sub_description)
  res = validate_sub(server, sub_id)
  validated_correctly = (res['validated'] == desired_result)
  delete_sub(server, sub_id)
  return validated_correctly

# Tests
def test_validator(server):

  # A receipt must be nonempty
  assert(run_a_validation(server, "", False))
  # A receipt must have at least one data line
  assert(run_a_validation(server, "program\tproject\tcenter\tsubmitter", False))
  # A receipt must not have extra or missing data columns 
  assert(run_a_validation(server, "program\tproject\tcenter\tsubmitter\nTEST\nTEST", False))
  assert(run_a_validation(server, "program\tproject\nTEST\tTEST\tEXTRA", False))

