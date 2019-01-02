FROM python:3.5

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install sudo -y
RUN ./setup.sh

EXPOSE 5000

ENV FLASK_APP __init__.py
ENV FLASK_ENV development

ENTRYPOINT ["flask", "run"]
