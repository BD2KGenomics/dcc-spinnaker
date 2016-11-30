import sys
import csv  # parse receipt
import logging
import redwood_client_lite

# python validation_engine.py receipt.tsv

'''
Validation Engine
'''


# Takes: information about a submission
# returns : a ValidationResult
def run_validations(receipt):
    result = validate_ReceiptFormat(receipt)
    if not(result.validated):
        return result
    result = validate_FileExists(receipt)
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
Validation Functions

Mandatory signature:

def validate_[what does this validate?](receipt)
return ValidationResult

receipt is a string containing the csv receipt document.

'''


# For each item in the receipt
# Checks that the metadata.json exists
def validate_FileExists(receipt):

    # Parameters - replicates ucsc-download.sh
    BASE_URL = "https://storage2.ucsc-cgl.org:5431"
    ACCESS_TOKEN = "/app/validator-downloader/accessToken"

    def validate(receipt):
        receipt_arr = receipt.split('\n')
        reader = csv.DictReader(receipt_arr, delimiter='\t')
        for row in reader:
            # Get file info from the receipt, returning a bad result if unable
            bad_receipt_result = ValidationResult(
                False,
                "Missing metadata ID, file ID, or bundle ID for a row in this receipt!")
            try:
                file_uuid = row['file_uuid']
                metadata = row['metadata_uuid']
                bundle = row['bundle_uuid']
            except KeyError:
                return bad_receipt_result
            if not(metadata and bundle and file_uuid):
                return bad_receipt_result

            # Download the metadata and check it for emptyiness
            try:
                downloaded_json = download_file(metadata, False)
            except redwood_client_lite.RedwoodServerError as error:
                return ValidationResult(
                    False,
                    "Failed to download metadata.json %s: Server error: %s." % (metadata, error))
            if not downloaded_json:
                return ValidationResult(False, "metadata.json file %s was empty." % metadata)
            if not check_downloaded_json(downloaded_json):
                return ValidationResult(False, "Downloaded json %s is not valid." % metadata)

            # Also download and check the beginning of the data file
            try:
                downloaded_file = download_file(file_uuid, True)
            except redwood_client_lite.RedwoodServerError as error:
                return ValidationResult(
                    False,
                    "Failed to download data file %s: Server error: %s." % (file_uuid, error))
            if not downloaded_file:
                return ValidationResult(False, "Data file %s was empty." % file_uuid)
            if not check_downloaded_file(downloaded_file):
                return ValidationResult(False, "Downloaded file %s is not valid." % file_uuid)
        # All files downloaded ok
        return ValidationResult(True)

    # use the python redwood client to download
    # a file and return the contents.
    # partial_download : if True, downloads the beginning of the file, as binary.
    # Otherwise, downloads the entire file as json.
    # TODO : is this really the best way to specify?
    def download_file(uuid, partial_download):
        # Get the access token
        try:
            with open(ACCESS_TOKEN, "r") as tokenfile:
                token = tokenfile.read().rstrip()
        except IOError:
            logging.info("Couldn't find download access token at path {}".format(ACCESS_TOKEN))
            return False

        if partial_download:
            result = redwood_client_lite.download_partial_file(BASE_URL, uuid, token)
        else:
            result = redwood_client_lite.download_json(BASE_URL, uuid, token)
        return result

    def check_downloaded_json(json):
        # TODO : inspect the json to see if it meets
        # some sort of standards
        return True

    def check_downloaded_file(file_contents):
        # TODO - meet some sort of standard?
        # For now, just confirm that it is nonempty by returning the contents back
        # since it will be checked for truthiness
        return file_contents
    return validate(receipt)


# Validate receipt for correct formatting
# and also if the fields match the specification given
# TODO confirm that this is necessary & sufficient
# Might a receipt have extra fields?
def validate_ReceiptFormat(receipt):
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


# Fake validation for testing
def validate_AlwaysSucceedsValidation(receipt):
    return ValidationResult(True, "Test validation suceeded.")


if __name__ == "__main__":
    with open(sys.argv[1], "r") as receipt:
        result = run_validations(receipt.read())
        if result.validated:
            print "Validated:"
        else:
            print "Failed validation:"
        print result.response
