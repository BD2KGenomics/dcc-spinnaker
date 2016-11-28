import time  # TODO : for testing only
import csv  # parse receipt
import logging
import redwood_client_lite

'''
Validation Engine
'''


# Takes: information about a submission
# returns : a ValidationResult
def validate(receipt):
    result = ReceiptFormatValidation().validate(receipt)
    if not(result.validated):
        return result
    result = FileExistsValidation().validate(receipt)
    return result


'''
Result of a validation.
validated : Boolean
response : String
'''


class ValidationResult():
    def __init__(self, validated, response=""):
        self.validated = validated
        self.response = response
        # TODO : validated must be True or False
        # if validated is false, response must be non-empty
        # (what was the error?)


'''
Validation Classes

'''


class FileExistsValidation():

    # Parameters - replicates ucsc-download.sh
    BASE_URL = "https://storage2.ucsc-cgl.org:5431"
    ACCESS_TOKEN = "/app/validator-downloader/accessToken"

    def validate(self, receipt):
        receipt_arr = receipt.split('\n')
        reader = csv.DictReader(receipt_arr, delimiter='\t')
        for row in reader:
            # Get the metadata uuid and bundle uuid.
            metadata = row['metadata_uuid']
            bundle = row['bundle_uuid']
            if not(metadata and bundle):
                return ValidationResult(
                    False,
                    "Missing metadata ID or bundle ID for a row in this receipt!")
            print metadata
            # Set up the download
            downloaded_json = self.download_file(metadata)
            if not downloaded_json:
                return ValidationResult(False, "Failed to download file.")
            # Check if it exists
            if not self.check_downloaded_file(downloaded_json):
                return ValidationResult(False, "Couldn't find downloaded file.")
        # All files downloaded ok
        return ValidationResult(True)

    # use the python redwood client to download
    # the metadata file and return it
    def download_file(self, uuid):
        # Get the access token
        try:
            with open(self.ACCESS_TOKEN, "r") as tokenfile:
                token = tokenfile.read().rstrip()
        except IOError:
            logging.info("Couldn't find download access token at path {}".format(self.ACCESS_TOKEN))
            return False

        # TODO : parse the uuid and ensure it's really a UUID here, to save some time
        # as the jar would reject it

        result = redwood_client_lite.download_json(self.BASE_URL, uuid, token)
        return result

    def check_downloaded_file(self, json):
        # TODO : inspect the json to see if it meets
        # some sort of standards
        return True


# Validate receipt for correct formatting
# and also if the fields match the specification given
# TODO confirm that this is necessary & sufficient
# Might a receipt have extra fields?
class ReceiptFormatValidation():
    def validate(self, receipt):
        # Attempt to parse the receipt as a tsv file with a header line
        receipt_arr = receipt.split('\n')
        # Receipt must have at least 2 rows (header + 1 data line)
        if len(receipt_arr) < 2:
            return ValidationResult(
                False,
                "Receipt must contain a header and at least one data line!")

        reader = csv.DictReader(receipt_arr, delimiter='\t')
        # Fields must be populated
        if not reader.fieldnames:
            return ValidationResult(
                False,
                "Receipt header must have at least 1 column!")

        # TODO fields must match the spec

        # Check for missing or extra data fields
        for row in reader:
            if None in row.values():
                return ValidationResult(
                    False,
                    "Receipt data line is missing at least 1 column!")
            if None in row.keys():
                return ValidationResult(
                    False,
                    "Receipt data line has at least 1 extra column!")

            logging.info(row)  # TODO don't print this
        # TODO : account for potential DOS line endings
        # TODO : fix encoding to be ASCII / UTF-8? Per:
        # https://docs.python.org/2/library/csv.html#csv-examples
        return ValidationResult(True, "Receipt validated ok.")


# Some validations to test with
class TestingValidation():
    def validate(self, receipt):
        if(receipt == "TEST_FAIL"):
            result = ValidationResult(False, "Fake failure for testing")
        elif(receipt == "TEST_SLOW_VALIDATE"):
            time.sleep(3)
            result = ValidationResult(False, "Fake delay for testing")
        else:
            result = ValidationResult(True, None)
        return result


class AlwaysFailsValidation():
    def validate(self, receipt):
        return ValidationResult(
            False,
            "This is a fake failure result for testing.")


class AlwaysSucceedsValidation():
    def validate(self, receipt):
        return ValidationResult(True)
