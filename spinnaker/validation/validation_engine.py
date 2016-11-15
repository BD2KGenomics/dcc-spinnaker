import time # TODO : for testing only
import csv # parse receipt
import logging

'''
Validation Engine
'''

# Takes: information about a submission
# returns : a ValidationResult
def validate(submission):
  #result = TestingValidation().validate(submission)
  result = ReceiptValidation().validate(submission)
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
    # If validated is False, the response must be a string
    # (ie, error responses are mandatory; but success responses


'''
Validation Classes

'''

# Validate receipt for correct formatting
class ReceiptValidation():

  def validate(self, receipt):

    # Attempt to parse the receipt as a tsv file with a header line
    receipt_arr = receipt.split('\n')
    # Receipt must have at least 2 rows (header + 1 data line) 
    if len(receipt_arr) < 2 :
      return ValidationResult(False, "Receipt must contain a header and at least one data line!")

    reader = csv.DictReader(receipt_arr, delimiter='\t')
    # Fields must be populated
    if not reader.fieldnames:
      return ValidationResult(False, "Receipt header must have at least 1 column!")
    # Check for missing or extra data fields 
    for row in reader:
      if None in row.values():
        return ValidationResult(False, "Receipt data line is missing at least 1 column!")
      if None in row.keys():
        return ValidationResult(False, "Receipt data line has at least 1 extra column!")


      logging.info(row) # TODO don't print this
    # TODO : account for potential DOS line endings
    # TODO : fix encoding to be ASCII / UTF-8? Per:
    # https://docs.python.org/2/library/csv.html#csv-examples
    # TODO... is the receipt nonempty
    # is the receipt correctly formatted
    # find a file(s) in it
    # see if they exist!
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
    return ValidationResult(False, "This is a fake failure result for testing.")

class AlwaysSucceedsValidation():
  def validate(self, receipt):
    return ValidationResult(True)
