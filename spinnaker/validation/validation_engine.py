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
error : String; or None if validated is True
'''
class ValidationResult():
  def __init__(self, validated, error=None):
    self.validated = validated
    self.error = error
    # TODO : validated must be True or False
    # If validated is true: error is None
    # Otherwise error is (TODO: ? non-empty string? ValidationError?)


'''
Validation Classes

'''
# Some validations to test with
class TestingValidation():
  def validate(self, submission):
    if(submission == "TEST_FAIL"):
      result = ValidationResult(False, "Fake failure for testing")
    elif(submission == "TEST_SLOW_VALIDATE"):
      time.sleep(3)
      result = ValidationResult(False, "Fake delay for testing")
    else:
      result = ValidationResult(True, None)
    return result

class AlwaysFailsValidation():
  def validate(self, submission):
    return ValidationResult(False, "This is a fake failure result for testing.")

class AlwaysSucceedsValidation():
  def validate(self, submission):
    return ValidationResult(True)
