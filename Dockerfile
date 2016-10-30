FROM alpine
RUN apk add --update make g++
RUN apk add --update python py-pip python-dev
RUN pip install --upgrade pip


WORKDIR /app
RUN apk add --update uwsgi-python
RUN apk add --update postgresql-dev
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

EXPOSE 5000

CMD uwsgi --ini uwsgi.ini
