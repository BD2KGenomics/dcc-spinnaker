import datetime
import logging
from flask import Flask, request, make_response
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Resource, Api, reqparse

from validation import validation_engine

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


# Run some testing validations
# TODO ultimately this will most likely not be a route
@app.route("/v0/validate/<submission_id>")
def validate(submission_id):
    submission = Submission.query.get(submission_id)
    if submission:
        # TODO : pass receipt info instead of description
        receipt = submission.description
    else:
        return make_response(jsonify(
            message="Submission {} does not exist".format(submission_id)), 404)

    # Run the validation
    validation_result = validation_engine.validate(receipt)

    # TODO : update submission state in DB once that field exists

    did_validate = validation_result.validated

    if(did_validate):
        message = "Validated!"
    else:
        message = "Failed validation: %s" % validation_result.response
    return make_response(jsonify(message=message, validated=did_validate), 200)


if __name__ == "__main__":
    manager.run()
