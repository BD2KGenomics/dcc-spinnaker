import sys
import os
import inspect
import csv  # parse receipt
import logging
import redwood_client_lite

# python validation_engine.py receipt.tsv

'''
Validation Engine
'''


# Takes: The receipt.tsv provided by the spinnaker client
# Finds all validation_ functions in this module, and runs them in roughly alphabetical order
# if a validation fails, returns that failed result & stops
# otherwise returns last succeeded validation
def run_validations(receipt):

    all_functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    validations = filter(lambda (name, fun): name.startswith("validate_"), all_functions)
    # Placeholder in case there are no validations.
    result = ValidationResult(False, "No validations were found for this submission!")

    for (name, function) in validations:
        result = function(receipt)
        if not(result.validated):
            return result
    return result


'''
Result of a validation.
validated : Boolean
response : String - a general class of response
details : String, optional - a more specific response that may mention submission-specific details.
'''


class ValidationResult():

    # Result strings that might be returned

    # Failure
    RECEIPT_MISSING_MD_FILE_OR_BUNDLE = (
        "Missing metadata ID, file ID, or bundle ID for a row in this receipt!")
    RECEIPT_TOO_SHORT = (
            "Receipt must contain a header and at least one data line!")
    RECEIPT_NO_HEADER = (
            "Receipt header must have at least 1 column!")
    RECEIPT_MISSING_DATA_COL = (
                "Receipt data line is missing at least 1 column!")
    RECEIPT_EXTRA_DATA_COL = (
                "Receipt data line has at least 1 extra column!")

    # TODO : make these more granular
    BAD_DOWNLOAD_METADATA = ("Metadata.json failed to download.")
    BAD_DOWNLOAD_DATA = ("Data file failed to download.")

    # Success
    RECEIPT_OK = "Receipt validated ok."

    def __init__(self, validated, response="", details=""):
        self.validated = validated
        self.response = response
        self.details = details
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
def validate_bbb_FileExists(receipt):

    # Parameters - replicates ucsc-download.sh
    #BASE_URL = "https://storage2.ucsc-cgl.org:5431"
    #BASE_URL = "storage.emily-dev.ucsc-cgl.org"
    #if not os.getenv("BASE_URL"):
    #    logging.error("Must set BASE_URL")
    #    return False
    #BASE_URL = "storage."+os.getenv("BASE_URL")
    BASE_URL = storage.emily.ucsc-cgp-dev.org
    def validate(receipt):
        receipt_arr = receipt.split('\n')
        reader = csv.DictReader(receipt_arr, delimiter='\t')
        for row in reader:
            # Get file info from the receipt, returning a bad result if unable
            bad_receipt_result = ValidationResult(
                False,
                ValidationResult.RECEIPT_MISSING_MD_FILE_OR_BUNDLE)
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
            except redwood_client_lite.RedwoodServerError:
                return ValidationResult(
                    False,
                    ValidationResult.BAD_DOWNLOAD_METADATA,
                    "Failed to download metadata.json {}".format(metadata))
            if not downloaded_json:
                return ValidationResult(False, ValidationResult.BAD_DOWNLOAD_METADATA,
                                        "metadata.json file %s was empty." % metadata)
            if not check_downloaded_json(downloaded_json):
                return ValidationResult(False, ValidationResult.BAD_DOWNLOAD_METADATA,
                                        "Downloaded json %s is not valid." % metadata)
            # Also download and check the beginning of the data file
            try:
                downloaded_file = download_file(file_uuid, True)
            except redwood_client_lite.RedwoodServerError:
                return ValidationResult(
                    False,
                    ValidationResult.BAD_DOWNLOAD_DATA,
                    "Failed to download data file {}".format(file_uuid))
            if not downloaded_file:
                return ValidationResult(False, ValidationResult.BAD_DOWNLOAD_DATA,
                                        "Data file %s was empty." % file_uuid)
            if not check_downloaded_file(downloaded_file):
                return ValidationResult(False, ValidationResult.BAD_DOWNLOAD_DATA,
                                        "Downloaded file %s is not valid." % file_uuid)
        # All files downloaded ok
        return ValidationResult(True)

    # use the python redwood client to download
    # a file and return the contents.
    # partial_download : if True, downloads the beginning of the file, as binary.
    # Otherwise, downloads the entire file as json.
    # TODO : is this really the best way to specify?
    def download_file(uuid, partial_download):
        # Get the access token
        if not os.getenv("UCSC_STORAGE_TOKEN"):
            logging.error("Must set UCSC_STORAGE_TOKEN")
            return False
        print("BASE_URL "+BASE_URL+" uuid "+uuid+" UCSC_STORAGE_TOKEN "+os.getenv("UCSC_STORAGE_TOKEN"))
        if partial_download:
            result = redwood_client_lite.download_partial_file(
                BASE_URL, uuid, os.getenv("UCSC_STORAGE_TOKEN"))
        else:
            result = redwood_client_lite.download_json(
                BASE_URL, uuid, os.getenv("UCSC_STORAGE_TOKEN"))
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
def validate_aaa_ReceiptFormat(receipt):
    # Attempt to parse the receipt as a tsv file with a header line
    receipt_arr = receipt.split('\n')
    # Receipt must have at least 2 rows (header + 1 data line)
    if len(receipt_arr) < 2:
        return ValidationResult(
            False,
            ValidationResult.RECEIPT_TOO_SHORT)

    reader = csv.DictReader(receipt_arr, delimiter='\t')
    # Fields must be populated
    if not reader.fieldnames:
        return ValidationResult(
            False, ValidationResult.RECEIPT_NO_HEADER)

    # TODO fields must match the spec

    # Check for missing or extra data fields
    for row in reader:
        if None in row.values():
            return ValidationResult(
                False, ValidationResult.RECEIPT_MISSING_DATA_COL)
        if None in row.keys():
            return ValidationResult(
                False, ValidationResult.RECEIPT_EXTRA_DATA_COL)

        logging.info(row)  # TODO don't print this
    # TODO : account for potential DOS line endings
    # TODO : fix encoding to be ASCII / UTF-8? Per:
    # https://docs.python.org/2/library/csv.html#csv-examples
    return ValidationResult(True, ValidationResult.RECEIPT_OK)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as receipt:
            res = run_validations(receipt.read())
            if res.validated:
                print "Validated:"
            else:
                print "Failed validation:"
            print res.response
    else:
        print("Usage: python validation_engine.py receipt.tsv")
