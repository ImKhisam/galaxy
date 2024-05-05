FROM python:3.10-slim

RUN mkdir site
WORKDIR site

ADD requirements.txt /site/
RUN pip3 install -r requirements.txt

ADD . /site/
ADD .env.docker /site/.env

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_NAME=DOCKER_DEMO

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN apt-get install ffmpeg -y

CMD python manage.py collectstatic \
    && gunicorn mysite.wsgi:application -b 0.0.0.0:8000

