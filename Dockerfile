# FROM mhart/alpine-node:7.1.0
FROM alpine
RUN apk add --update python py-pip
RUN pip install --upgrade pip


WORKDIR /app
RUN apk add --update uwsgi-python
# RUN apk add --update py-psycopg2
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Add bash for debugging convenience
RUN apk add --update bash 

# # Install yarn
# RUN mkdir -p /opt
# ADD latest.tar.gz /opt/
# RUN mv /opt/dist /opt/yarn
# ENV PATH "$PATH:/opt/yarn/bin"

# Add app code
ADD . /app

EXPOSE 5000

CMD uwsgi --ini uwsgi.ini
