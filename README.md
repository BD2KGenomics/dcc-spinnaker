[![Build Status](https://travis-ci.org/BD2KGenomics/spinnaker.svg?branch=master)](https://travis-ci.org/BD2KGenomics/spinnaker)

# Spinnaker Server
Receives receipts from the spinnaker upload client and validates the data

# Build, Debug and Test Locally

Build a local docker container:

    make build

Initialize a new database,b


Start a cgtd container linked to the ipfs container:

    make debug

This runs the cgtd container listening on port 5000 out of the local folder so
you can make changes and it will live reload.

To run tests open another terminal window and:

    make test

# Running a Production Instance

Note: The only dependencies for the following is make and docker

Create an initialize a database in the /data folder

   make init migrate


Startup the spinnaker container listening on port 5000

    make run

Get a list of submissions

    curl localhost:5000/v0/submissions

# Making Submissions

To make a test submission:

    make submit

or via curl:

    docker exec -it cgtd curl -X POST localhost:5000/v0/submissions \
        -F "a_field_name=a_field_value" \
        -F files[]=@tests/ALL/SSM-PAKMVD-09A-01D.vcf

To access the submission:

    curl localhost/v0/submissions/QmZwuc83iD64mvsf484aGcerUHJce1bJtf1y7AAzQDp234

Access control for mutable operations such as adding submissions or peers
is restricted to localhost as a poor mans authentication. As a result we curl
from within the cgtd container above.

To populate a server with a bunch of test data:

    make populate

Finally to see the index for you server including submissions:

    curl localhost/v0/submissions

