FROM alpine:3.5
RUN apk add --update python py2-pip
RUN pip install --upgrade pip

WORKDIR /app
RUN apk add --update uwsgi-python py-psycopg2
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add bash for debugging convenience
RUN apk add --update bash 

# Add app code
ADD . /app

EXPOSE 5000

CMD uwsgi --ini uwsgi.ini
