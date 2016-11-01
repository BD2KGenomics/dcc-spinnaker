import datetime
import logging
from flask import Flask, request
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Resource, Api

app = Flask(__name__, static_url_path="")
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/foo")
def foo():
    raise
    return "Hello"


"""
Database
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


@api.route("/v0/submissions")
class SubmissionsCollection(Resource):

    def get(self):
        """
        Return a list of all submissions.
        """
        return jsonify(submissions=[s.to_dict() for s in Submission.query.all()])

    def post(self):
        """
        Creates a new submission
        """
        logging.info("Creating a new submission")
        fields = request.get_json()
        submission = Submission(description=fields["description"])
        db.session.add(submission)
        db.session.commit()
        return jsonify(submission=submission.to_dict())


if __name__ == "__main__":
    manager.run()
