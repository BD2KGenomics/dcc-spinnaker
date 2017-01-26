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


# Build, Debug and Test Locally

Start the database container:

    make db

Create the database if it doens't exist and apply any migrations:

    make upgrade

Build a local spinnaker docker container:

    make build

Run a debug server

    make debug

This runs the spinnaker container listening on port 5000 out of the local folder so
you can make changes and it will live reload.

To run tests open another terminal window and:

    make test

# Database Migrations

After making changes to the model:

    make migrate

which will create a new migration in /migrations which will get applied via make upgrade

# API

To view the swagger REST API documentation open a browser to <server>/api

# Running Behind HTTPS Auth Proxy

1. Obtain a domain name and point to your server.
2. Obtain a certificate for that domain. LetsEncrypt is highly recommended. https://certbot.eff.org/#ubuntuxenial-other
3. Place certificate in a `cert` directory in the root this project
4. Create an accessControl.json file
   should look something like this, anyone who has any privilege for a service will be forwarded on
   w/ their email and a list of privileges as headers
    ```
    
    {
      "jane@example.com": ["spinnaker.user", "spinnaker.admin"]
      "bob@example.com": ["spinnaker.user"]
      "barbara@example.com": ["spinnaker.user"]
    }
    ```
4. Pick a subdomain for your proxy server (e.g. proxy.example.com) and add it to your DNS
5. Create an OAuth2 app using the Google developer console.
   a) Add https://PROXYSUBDOMAIN/auth/google/callback s a callback url
   b) ensure the Google Plus API is enabled (this is how user's profile information is obtained)
6. Make sure you have defined the following environment variables defined
    ```
     GOOGLE_CLIENT_ID # obtain from Google Developer Console
     GOOGLE_CLIENT_SECRET # obtain from Google Developer Console
     SESSION_SECRET
     COOKIE_DOMAIN # most likely your root domain e.g. example.com
     HOST # your proxy subdomain (e.g. proxy.example.com)
```
7. Run with `docker-compose up`
