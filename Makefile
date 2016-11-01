build:
	docker build -t ucsc/spinnaker .

init:
	sudo rm -rf migrations data
	mkdir -p data
	docker run -it --rm -v `pwd`:/app -v `pwd`/data:/data ucsc/spinnaker python spinnaker/spinnaker.py db init

migrate:
	docker run -it --rm -v `pwd`:/app -v `pwd`/data:/data ucsc/spinnaker python spinnaker/spinnaker.py db migrate
	docker run -it --rm -v `pwd`:/app -v `pwd`/data:/data ucsc/spinnaker python spinnaker/spinnaker.py db upgrade

debug:
	# Run spinnaker out of the current directory with reloading after code change
	docker run --name spinnaker --rm -it \
		-v `pwd`:/app \
		-v `pwd`/data:/data \
		-p 5000:5000 \
		-e FLASK_DEBUG='True' \
		ucsc/spinnaker python spinnaker/spinnaker.py runserver --host 0.0.0.0
		# To run in uwsgi with reloading use the following, but flask debugger doesn't work...
		# ucsc/spinnaker uwsgi --ini uwsgi.ini --honour-stdin --python-autoreload=1 --processes=1 --threads=1

run:
	# Run using the built image with multiple processes and threads with uwsgi
	docker run -it --rm -v `pwd`/data:/data ucsc/spinnaker python spinnaker/spinnaker.py db upgrade
	docker run --name spinnaker -it --rm -v `pwd`/data:/data -p 5000:5000 ucsc/spinnaker 

test:
	# Run pytest inside the running container from debug or run
	docker exec spinnaker py.test -p no:cacheprovider -s -x

stop:
	docker stop spinnaker || true && docker rm spinnaker || true
