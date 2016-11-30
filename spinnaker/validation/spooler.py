import sys
# Get the validation_engine imported
sys.path.append("/app/spinnaker/validation")
import validation_engine
import uwsgi

'''
uwsgi spooler
'''


def spooler(items):
    # This takes the receipt
    # then runs - asynchronously - the validations
    print "Spooler callback function is running!"
    print items
    return uwsgi.SPOOL_OK
    # uwsgi.SPOOL_RETRY, SPOOL_IGNORE

uwsgi.spooler = spooler
