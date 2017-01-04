from spinnaker.validation import validation_engine
from spinnaker.validation.validation_engine import ValidationResult as VR
# Tests for the validator
# Calls the validator module directly; does NOT interact with the spooler.

# Helper functions


# Create a submission, validate it, and delete it.
# Returns whether the validation result was the desired_result
# This checks both validated (Y/N) and the particular result type
# (Does not check response details)
def run_a_validation(receipt, should_validate, should_have_reason):
    result = validation_engine.run_validations(receipt)
    validated_correctly = ((result.validated == should_validate)
                           and (result.response == should_have_reason))
    if not validated_correctly:
        print result.response
    return validated_correctly


# Tests
def test_validator():

    # Receipt format validator

    # A receipt must be nonempty
    assert(run_a_validation("", False, VR.RECEIPT_TOO_SHORT))
    # A receipt must have at least one data line
    assert(run_a_validation("program\tproject\tcenter\tsubmitter", False, VR.RECEIPT_TOO_SHORT))
    # A receipt must have at least one header column
    assert(run_a_validation("\nTEST\tTEST", False, VR.RECEIPT_NO_HEADER))
    # A receipt must not have extra or missing data columns
    assert(run_a_validation("program\tproject\tcenter\tsubmitter\nTEST\nTEST", False,
                            VR.RECEIPT_MISSING_DATA_COL))
    assert(run_a_validation("program\tproject\nTEST\tTEST\tEXTRA", False,
                            VR.RECEIPT_EXTRA_DATA_COL))

    # File exists validator

    # Missing file-specific columns
    assert(run_a_validation("program\tproject\nTEST program\tTEST project", False,
                            VR.RECEIPT_MISSING_MD_FILE_OR_BUNDLE))

    # TODO : test to distinguish between a bad file, and a missing access token.

    # Try to download nonexistant file
    assert(run_a_validation("file_uuid\tmetadata_uuid\tbundle_uuid\n"
                            "TEST file\tTEST md\tTEST bundle", False,
                            VR.BAD_DOWNLOAD_METADATA))

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
