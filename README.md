[![Build Status](https://travis-ci.org/BD2KGenomics/dcc-spinnaker.svg?branch=master)](https://travis-ci.org/BD2KGenomics/dcc-spinnaker)
[![Docker Repository on Quay](https://quay.io/repository/ucsc_cgl/dcc-spinnaker/status "Docker
Repository on Quay")](https://quay.io/repository/ucsc_cgl/dcc-spinnaker)

# Spinnaker Server
Receives receipts from the spinnaker upload client and validates the submissions

# Environment

Spinnaker accesses the storage system when validating submissions via
a token stored in the UCSC_STORAGE_TOKEN environment file.

# Run

    docker-compose up

NOTE: Server listens on 5000 but the port is not exposed
as we assume a proxy will be in front of the server in production
and linked via docker.

# Build, Debug and Test Locally

Build out of the local folder

    make build

Start the database and server running out of the current directory
with auto reload:

    make debug

Create the database if it doens't exist and apply any migrations:

    make upgrade

To run tests open another terminal window and:

    make test

# Database Migrations

After making changes to the model:

    make migrate

which will create a new migration in /migrations which will get 
applied via make upgrade which is automatically called in the 
production server on startup.

# API

To view the swagger REST API documentation open a browser to <server>/api
