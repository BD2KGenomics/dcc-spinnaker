build:
	# Build spinnaker into a local container
	docker build -t quay.io/ucsc_cgl/dcc-spinnaker .

debug:
	# Run using the local files for debugging with auto-reloading
	docker run --name spinnaker --rm -it \
		-v `pwd`:/app \
		--link db:db \
		-p 5000:5000 \
		-e FLASK_DEBUG='True' \
		-e UCSC_DCC_TOKEN=$(UCSC_DCC_TOKEN) \
		ucsc/spinnaker uwsgi --ini uwsgi.ini --honour-stdin --python-autoreload=1 --processes=1 --threads=1

run:
	# Apply migrations and then run using the built image in daemon mode
	docker-compose up

test:
	# Run pytest inside the running container from debug or run
	docker exec dccspinnaker_spinnaker_1 py.test -p no:cacheprovider -s -x

db:
	# Run a local postgres database in a container
	docker run -d --name db \
          -v `pwd`/data:/var/lib/postgresql/data \
          -e POSTGRES_PASSWORD=gi123 \
          -e POSTGRES_USER=spinnaker \
          -e POSTGRES_DB=spinnaker \
          postgres

upgrade:
	# Create the database if it doesn't exist and apply any migrations if it does
	docker run -it --rm -v `pwd`:/app --link db:db ucsc/spinnaker python spinnaker/spinnaker.py db upgrade

migrate:
	# Create any required migrations
	docker run -it --rm -v `pwd`:/app --link db:db quay.io/ucsc_cgl/dcc-spinnaker python spinnaker/spinnaker.py db migrate

reset:
	docker-compose stop
	docker-compose rm -f
	docker volume rm dccspinnaker_postgres
