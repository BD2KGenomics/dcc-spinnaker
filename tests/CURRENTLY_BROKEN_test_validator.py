import json
import requests
# Tests for the validator

# TODO : none of these will work any more because
# all the validations run asynchronously now and the
# endpoint is changed.
#  change it to not interact with the server
# and just call the validation module directly.

# Helper functions


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


# returns submission ID
def insert_sub(server, sub_receipt):
    r = requests.post(url_for(server, "submissions"),
                      json={"receipt": sub_receipt})
    submission = json.loads(r.text)["submission"]
    return submission["id"]


def delete_sub(server, sub_id):
    requests.delete(url_for(server, "submissions/{}".format(sub_id)))


# Takes ID, returns the result json
def validate_sub(server, sub_id):
    r = requests.get(url_for(server, "validation/{}".format(sub_id)))
    return json.loads(r.text)


# Create a submission, validate it, and delete it.
# Returns whether the validation result was the desired_result
def run_a_validation(server, sub_receipt, desired_result):
    sub_id = insert_sub(server, sub_receipt)
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

    # TODO: more tests to write
    # A receipt must have all of the appropriate column headers (extras are ok)
    #         fieldnames = ["program"    #  "project"
    #  "center_name"
    #  "submitter_donor_id"
    #  "donor_uuid"
    #  "submitter_specimen_id"
    #  "specimen_uuid"
    #  "submitter_specimen_type"
    #  "submitter_sample_id"
    #  "sample_uuid"
    #  "analysis_type"
    #  "workflow_name"
    #  "workflow_version"
    #  "file_type"
    #  "file_path"
    #  "file_uuid"
    #  "bundle_uuid"
    #  "metadata_uuid"]

    # Test the file download validator :
    # won't download :
    # ok receipt format, not a uuid
    # ok receipt format, bad file uuid ( doesn't exist)

    # downloads but won't check :
    # ok receipt format, ok file uuid, but bad bundle id or file name
