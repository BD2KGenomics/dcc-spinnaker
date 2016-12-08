build:
	docker build -t ucsc/spinnaker .

db:
	docker run -d --name db \
          -v `pwd`/data:/var/lib/postgresql/data \
          -e POSTGRES_PASSWORD=gi123 \
          -e POSTGRES_USER=spinnaker \
          -e POSTGRES_DB=spinnaker \
          postgres


reset: delete_db migrate upgrade

delete_db:
	docker exec -it db dropdb -U spinnaker spinnaker || true
	docker exec -it db createdb -U spinnaker spinnaker || true
	sudo rm -rf migrations || true
	docker run -it --rm -v `pwd`:/app --link db:db ucsc/spinnaker python spinnaker/spinnaker.py db init

upgrade:
	# Create the database if it doesn't exist and apply any migrations if it does
	docker run -it --rm -v `pwd`:/app --link db:db ucsc/spinnaker python spinnaker/spinnaker.py db upgrade

migrate:
	# Create any required migrations
	docker run -it --rm -v `pwd`:/app --link db:db ucsc/spinnaker python spinnaker/spinnaker.py db migrate

debug:
	# Run using the local files for debugging with auto-reloading
	docker run --name spinnaker --rm -it \
		-v `pwd`:/app \
		--link db:db \
		-p 5000:5000 \
		-e FLASK_DEBUG='True' \
		ucsc/spinnaker uwsgi --ini uwsgi.ini --honour-stdin --python-autoreload=1 --processes=1 --threads=1
		#ucsc/spinnaker python spinnaker/spinnaker.py runserver --host 0.0.0.0
		# To run in uwsgi with reloading use the following, but flask debugger doesn't work...
		# ucsc/spinnaker uwsgi --ini uwsgi.ini --honour-stdin --python-autoreload=1 --processes=1 --threads=1

run:
	# Apply migrations and then run using the built image in daemon mode
	docker run -it --rm --link db:db ucsc/spinnaker python spinnaker/spinnaker.py db upgrade
	docker run --name spinnaker -d --link db:db -p 5000:5000 ucsc/spinnaker

edit:
	# Mount the local files WITHOUT auto-reload, and ssh in. For manually twiddling the files in the docker context
	# without losing your box every time you make a syntax error.
	docker run --name spinnaker -d \
		-v `pwd`:/app \
		-v `pwd`/data:/data \
		-p 5000:5000 ucsc/spinnaker
	docker exec -it spinnaker /bin/bash

stop:
	docker stop spinnaker || true && docker rm spinnaker || true
	docker stop db || true && docker rm db || true

test:
	# Run pytest inside the running container from debug or run
	docker exec spinnaker py.test -p no:cacheprovider -s -x
