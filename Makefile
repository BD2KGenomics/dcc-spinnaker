stop:
	docker stop spinnaker || true && docker rm spinnaker || true
	# docker stop postgres || true && docker rm postgres || true

build:
	docker build -t ucsc/spinnaker .

db:
	# Start postgres docker container
	docker run -d --name postgres \
		-v /tmp/postgres:/var/lib/postgresql/data \
		-e POSTGRES_PASSWORD=password \
		-e POSTGRES_USER=default \
		-e POSTGRES_DB=spinnaker \
		postgres

    # debug(cmd="python spinnaker/spinnaker.py db upgrade")


debug:
	# Run spinnaker out of the current directory with reloading after code change
	docker run --name spinnaker --rm -it \
		-v `pwd`:/app:ro \
		-p 5000:5000 \
		ucsc/spinnaker uwsgi --ini uwsgi.ini --python-autoreload=1 --processes=1 --threads=1

test:
	docker exec spinnaker py.test -p no:cacheprovider -s -x

run:
	# Run the latest built version from docker hub
	docker run -d --name spinnaker --link ipfs:ipfs -p 80:5000 ucsc/spinnaker
