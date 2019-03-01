# This file allows you to build a docker container:
# sudo docker build .
# sudo docker run together

# FROM python:3.5
# FROM selenium/node-chrome:3.141.59-dubnium
FROM robcherry/docker-chromedriver:latest

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install sudo -y
RUN apt-get install python-setuptools python-dev build-essential -y 
RUN sudo easy_install pip
RUN ./setup.sh
RUN echo 'Setup complete. Exposing port 5000.'

EXPOSE 5000

ENV FLASK_APP __init__.py
ENV FLASK_ENV development

ENTRYPOINT ["flask", "run"]
