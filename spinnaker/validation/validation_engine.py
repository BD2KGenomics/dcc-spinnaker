import time # TODO : for testing only

'''
Validation Engine
'''

# Takes: information about a submission
# returns : a ValidationResult
def validate(submission):
  result = TestingValidation().validate(submission)
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

# Attempt at a "real" validation
class ValidateRecipt():
  def validate(self, receipt):
    # is the receipt nonempty
    # is the receipt correctly formatted
    # find a file(s) in it
    # see if they exist!
    return ValidationResult(False, "NYI")

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
