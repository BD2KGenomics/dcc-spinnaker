# for the validator-downloader: use alpine with java8 jre installed instead
# FROM mhart/alpine-node:7.1.0
# FROM alpine
FROM openjdk:8-jre-alpine

RUN apk add --update python py-pip
RUN pip install --upgrade pip


WORKDIR /app
RUN apk add --update uwsgi-python
# RUN apk add --update py-psycopg2
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# validator-downloader: also add bash
RUN apk add --update bash 

# # Install yarn
# RUN mkdir -p /opt
# ADD latest.tar.gz /opt/
# RUN mv /opt/dist /opt/yarn
# ENV PATH "$PATH:/opt/yarn/bin"

# Add app code
ADD . /app
# validator-downloader: TODO get the java code from Brian's download link
# for now, it needs to be added after checkout to the validator-downloader
# dir, along with the accessToken, because it is .gitignored.

EXPOSE 5000

CMD uwsgi --ini uwsgi.ini
