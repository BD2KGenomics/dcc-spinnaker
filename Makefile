build:
	docker build -t quay.io/ucsc_cgl/dcc-spinnaker .

debug:
	# Run out of local folder with reload
	docker-compose -f docker-compose-debug.yml up

run:
	# Apply migrations and then run using the built image in daemon mode
	docker-compose up

test:
	# Run pytest inside the running container from debug or run
	docker exec -it dccspinnaker_spinnaker_1 py.test -p no:cacheprovider -s -x

upgrade:
	# Create the database if it doesn't exist and apply any migrations if it does
	docker exec -it dccspinnaker_spinnaker_1 python spinnaker/spinnaker.py db upgrade

migrate:
	# Create any required migrations
	docker exec -it dccspinnaker_spinnaker_1 python spinnaker/spinnaker.py db migrate

stop:
	docker-compose -f docker-compose-debug.yml down

reset:
	docker-compose -f docker-compose-debug.yml stop
	docker-compose -f docker-compose-debug.yml rm -f
	docker volume rm dccspinnaker_postgres
