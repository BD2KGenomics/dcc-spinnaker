import sys
import datetime
import logging
import uuid
from flask import Flask, request, make_response
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Resource, Api, reqparse
import os
from flask import url_for
from flask import render_template

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)

# monkey patch courtesy of
# https://github.com/noirbizarre/flask-restplus/issues/54
# so that /swagger.json is served over https
if os.environ.get('HTTPS'):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')

    Api.specs_url = specs_url

"""
uwsgi is being used only to send async jobs to the spooler.
it's only available when the app is run in a uwsgi context.
Allow the app to be run outside of that context for other
tasks, eg db migration.
this MUST be after the logging.basicConfig or logging breaks.
"""
try:
    import uwsgi
except ImportError:
    logging.info("Couldn't import uwsgi.")


@app.route("/")
def index():
    logging.info("emily")
    #return app.send_static_file("index.html")
    return render_template("index.html")

"""
Database and Models
"""
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://{}:{}@db/spinnaker".format(
    os.getenv("POSTGRES_USER"), os.getenv("POSTGRES_PASSWORD"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


class Submission(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # status = db.Column(db.Enum("new", "received", "validated",
    #                            "invalid", "signed"), default="new")
    status = db.Column(db.Text, default="new")
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    receipt = db.Column(db.Text)
    validation_message = db.Column(db.Text)
    validation_details = db.Column(db.Text)

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
        """ Get a list of all submissions in reverse chronological order """
        return jsonify(submissions=[s.to_dict() for s in
                                    Submission.query.order_by(Submission.created.desc()).all()])

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


@api.route("/v0/validation/<id>")
class ValidationAPI(Resource):
    def get(self, id):
        """ Request a validation for a submission, without needing to update the receipt """
        # TODO: should confirm submission exists & has receipt
        if 'uwsgi' in sys.modules:
            uwsgi.spool({'submission_id': id})
        else:
            logging.debug("UWSGI not available; skipping validation of submission {}.".format(id))
        return make_response(jsonify(message="Submission {} queued for validation".format(id)), 200)

    # PUT validation: Accept bool validated and str response, and update the submission
    # with whether it validated or not.
    # TODO : if we plan to actually use this endpoint, set up a secret key system:
    # add to the Makefile generation of a random key that is available to both the
    # validator on the server & this file; then use this key to auth requests to the endpoint.
    @api.expect(json_parser)
    def put(self, id):
        """ Update a submission with the results of a validation """
        submission = Submission.query.get(id)
        logging.info(request.get_json())
        did_validate = request.get_json().get("validated")
        validation_message = request.get_json().get("response", "")
        validation_details = request.get_json().get("details", "")
        if submission:
            if did_validate:
                submission.status = "validated"
            else:
                submission.status = "invalid"
            # TODO : Save old validation messages somewhere?
            submission.validation_message = validation_message
            submission.validation_details = validation_details
            submission.modified = datetime.datetime.utcnow()
            db.session.commit()
            logging.info("Sub {}'s validation was {}: {}".format(
                id, did_validate, validation_message))
            return make_response(jsonify(
                message="Accepted validation result for {}: {}--".format(
                    id, did_validate, validation_message)), 200)
        else:
            return make_response(jsonify(message="Submission {} does not exist".format(id)), 404)


if __name__ == "__main__":
    manager.run()
