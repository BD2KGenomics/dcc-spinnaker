import sys
import datetime
import logging
from flask import Flask, request, make_response
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Resource, Api, reqparse

sys.path.append("/app/spinnaker")
from validation import validation_engine  # noqa: E402

# uwsgi is being used only to send async jobs to the spooler.
# it's only available when the app is run in a uwsgi context.
# Allow the app to be run outside of that context for other
# tasks, eg db migration.
# Do this after the logging is config so it we can log it.
try:
    import uwsgi
except ImportError:
    logging.info("Couldn't import uwsgi.")


app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    return app.send_static_file("index.html")


"""
Database and Models
"""
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/spinnaker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum("new", "received", "validated", "invalid", "signed"), default="new")
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    receipt = db.Column(db.Text)

    def to_dict(self):
        """ Annoyingly jsonify doesn't automatically just work... """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


"""
RESTful API
"""
api = Api(app, title="Spinnaker API", doc="/api", description="""
RESTful API for the Spinnaker submissions service

Source: https://github.com/BD2KGenomics/spinnaker
""")
app.config.SWAGGER_UI_JSONEDITOR = True

json_parser = reqparse.RequestParser()
json_parser.add_argument("json", location="json")


@api.route("/v0/submissions")
class SubmissionsAPI(Resource):

    def get(self):
        """ Get a list of all submissions """
        return jsonify(submissions=[s.to_dict() for s in Submission.query.all()])

    @api.expect(json_parser)
    def post(self):
        """ Create a new empty submission """
        fields = request.get_json()
        submission = Submission(**fields)
        db.session.add(submission)
        db.session.commit()
        logging.info("Created submission id {}".format(submission.id))
        return make_response(jsonify(submission=submission.to_dict()), 201)


@api.route("/v0/submissions/<id>")
class SubmissionAPI(Resource):

    def get(self, id):
        """ Get a submission """
        submission = Submission.query.get(id)
        if submission:
            return jsonify(submission=submission.to_dict())
        else:
            return make_response(jsonify(message="Submission {} does not exist".format(id)), 404)

    @api.expect(json_parser)
    def put(self, id):
        """ Edit a submission """
        submission = Submission.query.get(id)
        if submission:
            submission.receipt = request.get_json().get("receipt", submission.receipt)
            submission.status = "received"
            submission.modified = datetime.datetime.utcnow()
            db.session.commit()
            logging.info("Edited submission {}".format(id))
            # Asynchronously kick off the validate if available
            # The spooler callback will fetch the receipt and pass to the validator.
            if 'uwsgi' in sys.modules:
                uwsgi.spool({'submission_id': id})
            else:
                logging.debug("UWSGI not available; skipping validation.")
            return jsonify(submission=submission.to_dict())
        else:
            return make_response(jsonify(message="Submission {} does not exist".format(id)), 404)

    def delete(self, id):
        """ Delete a submission """
        submission = Submission.query.get(id)
        if submission:
            db.session.delete(submission)
            db.session.commit()
            logging.info("Deleted submission {}".format(id))
            return jsonify(message="Deleted submission {}".format(id))
        else:
            return make_response(jsonify(message="Submission {} does not exist".format(id)), 404)


"""
Validation Engine
"""


# Run a validation synchronously; doesn't need uWSGI
# TODO should this endpoint be included in the API?
@app.route("/v0/validate/<submission_id>")
def validate_endpoint(submission_id):
    (response_dict, response_code) = do_validate(submission_id)
    return make_response(jsonify(response_dict), response_code)


# Actually runs the validation & updates its database state.
# Outside of the Flask application context.
# Returns the tuple (response dict, http response code)
def do_validate(submission_id):
    submission = Submission.query.get(submission_id)
    if submission:
        receipt = submission.receipt
    else:
        return ({"message": "Submission {} does not exist".format(submission_id)}, 404)

    # Call the validation module
    validation_result = validation_engine.validate(receipt)

    if(validation_result.validated):
        submission.status = "validated"
        submission.modified = datetime.datetime.utcnow()
        db.session.commit()
        logging.info("Validated submission {}".format(submission_id))
        message = "Validated {}".format(validation_result.response)
    else:
        submission.status = "invalid"
        submission.modified = datetime.datetime.utcnow()
        db.session.commit()
        logging.info("Invalid submission {}".format(submission_id))
        message = "Failed validation: {}".format(validation_result.response)
    return ({"message": message, "validated": validation_result.validated}, 200)


'''
uwsgi spooler
'''


# uWSGI spooler callback function. Runs a validation for
# the submission whose ID is passed in as submission_id.
def spooler(job_info):
    logging.info("Spooler callback function is running!")
    logging.info(job_info)
    # Get the submisssion from the ID
    id = job_info['submission_id']
    result = do_validate(id)
    logging.info("Validation commpleted: %s : %s" % result)
    return uwsgi.SPOOL_OK


# Only register the callback when running in spooler environment
if 'uwsgi' in sys.modules:
    uwsgi.spooler = spooler
else:
    pass

if __name__ == "__main__":
    manager.run()
