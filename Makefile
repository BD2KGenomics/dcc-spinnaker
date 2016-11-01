build:
	docker build -t ucsc/spinnaker .

init:
	sudo rm -rf migrations data
	mkdir -p data
	docker run -it --rm -v `pwd`:/app ucsc/spinnaker python spinnaker/spinnaker.py db init

migrate:
	docker run -it --rm -v `pwd`:/app ucsc/spinnaker python spinnaker/spinnaker.py db migrate
	docker run -it --rm -v `pwd`:/app ucsc/spinnaker python spinnaker/spinnaker.py db upgrade

debug:
	# Run spinnaker out of the current directory with reloading after code change
	docker run --name spinnaker --rm -it \
		-v `pwd`:/app \
		-p 5000:5000 \
		ucsc/spinnaker python spinnaker/spinnaker.py 
		# in production we'll run under uwsgi but haven't sorted debugger in it
		# ucsc/spinnaker uwsgi --ini uwsgi.ini --honour-stdin --python-autoreload=1 --processes=1 --threads=1

test:
	# Run pytest inside the running container from debug or run
	docker exec spinnaker py.test -p no:cacheprovider -s -x

stop:
	docker stop spinnaker || true && docker rm spinnaker || true
