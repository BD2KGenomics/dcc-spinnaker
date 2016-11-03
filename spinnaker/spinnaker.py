import datetime
import logging
from flask import Flask, request, make_response
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Resource, Api, reqparse

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/debug")
def debug():
    """
    Throw an exception to show what the Flask debugger looks like.
    Haven't figured out how to make it work with Flask Restplus...
    """
    raise
    return "OK", 200


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
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

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
        """
        Return a list of all submissions.
        """
        return jsonify(submissions=[s.to_dict() for s in Submission.query.all()])

    @api.expect(json_parser)
    def post(self):
        """
        Creates a new submission
        """
        logging.info("Creating a new submission")
        fields = request.get_json()
        submission = Submission(description=fields["description"])
        db.session.add(submission)
        db.session.commit()
        return make_response(jsonify(submission=submission.to_dict()), 201)


@api.route("/v0/submissions/<id>")
class SubmissionAPI(Resource):

    def get(self, id):
        """
        Return a submission by uuid
        """
        submission = Submission.query.filter_by(id=id).one_or_none()
        if submission:
            return jsonify(submission=submission.to_dict())
        else:
            return make_response(jsonify(message="Submission {} does not exist".format(id)), 404)


if __name__ == "__main__":
    manager.run()
