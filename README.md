[![Build Status](https://travis-ci.org/BD2KGenomics/dcc-spinnaker.svg?branch=master)](https://travis-ci.org/BD2KGenomics/dcc-spinnaker)

# Spinnaker Server
Receives receipts from the spinnaker upload client and validates the data

# Build, Debug and Test Locally

Build a local docker container:

    make build

Run a debug server

    make debug

This runs the cgtd container listening on port 5000 out of the local folder so
you can make changes and it will live reload.

To run tests open another terminal window and:

    make test

# Submissions

To view all submissions in a browser navigate to <server>/submissions.html

Make a new submission:

    curl -H "Content-Type: application/json" -X POST -d '{"description": "dude"}' \
        localhost:5000/v0/submissions

Get a list of all submissions:

    curl localhost:5000/v0/submissions

# Database Migrations

After making changes to the model:

    make migrate

which will create a new migration in /migrations
