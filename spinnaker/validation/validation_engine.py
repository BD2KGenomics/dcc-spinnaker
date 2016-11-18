import time  # TODO : for testing only
import csv  # parse receipt
import logging
import subprocess  # for java call only
import os

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
    BASE_URL = "https://storage2.ucsc-cgl.org"
    DOWNLOAD_DIR = "/app/validator-downloader/"
    JAVA_DIR = "/app/validator-downloader/ucsc-storage-client/"
    SSL_DIR = "ssl/cacerts"
    JARNAME = "icgc-storage-client-1.0.14-SNAPSHOT/lib/icgc-storage-client.jar"
    ACCESS_TOKEN = "/app/validator-downloader/accessToken"

    def validate(self, receipt):
        receipt_arr = receipt.split('\n')
        reader = csv.DictReader(receipt_arr, delimiter='\t')
        for row in reader:
            # Get the metadata uuid and bundle uuid.
            metadata = row['metadata_uuid']
            bundle = row['bundle_uuid']
            metadata_filename = "metadata.json"
            if not(metadata and bundle):
                return ValidationResult(
                    False,
                    "Missing metadata ID or bundle ID for a row in this receipt!")
            print metadata
            # Set up the download
            if not self.download_file(metadata):
                return ValidationResult(False, "Failed to download file.")
            # Check if it exists
            if not self.check_downloaded_file(bundle, metadata_filename):
                return ValidationResult(False, "Couldn't find downloaded file.")
        # All files downloaded ok
        return ValidationResult(True)

    # Run a hardcoded system call to download the desired file.
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

        cmd = ("java -Djavax.net.ssl.trustStore=" + self.JAVA_DIR + self.SSL_DIR + " "
               "-Djavax.net.ssl.trustStorePassword=changeit "
               "-Dmetadata.url=" + self.BASE_URL + ":8444 -Dmetadata.ssl.enabled=true "
               "-Dclient.ssl.custom=false -Dstorage.url=" + self.BASE_URL + ":5431 "
               "-DaccessToken=" + token + " "
               "-jar " + self.JAVA_DIR + self.JARNAME + " "
               "download --output-dir " + self.DOWNLOAD_DIR + " --object-id " + uuid + " "
               "--output-layout bundle"
               )
        # TODO don't use shell=True but break the above cmd into key/value pairs
        retval = subprocess.call(cmd, shell=True)

        # TODO : is there a good way to get the bundle ID from the download output
        # so we can clean it up later if the metadata had it wrong
        # (Very unlikely with real data, so not high priority)
        return (retval == 0)

    # See if the named file exists in the bundle in the download dir
    def check_downloaded_file(self, bundle, filename):
        # Get path to file
        download_path = self.DOWNLOAD_DIR + bundle + "/" + filename
        try:
            with open(download_path, "r"):
                # TODO : Look at the contents of the file and
                # make some judgement about it
                pass
            # Clean up the downloaded file (whether it worked or not)
            os.remove(download_path)
            # TODO : also need to clean up the bundle directory at some point
            # but when ? might bundles persist over multiple lines of the receipt?
        except IOError as e:
            logging.info("I/O error({0}): {1}: {2}".format(e.errno, e.strerror, download_path))
            return False
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
