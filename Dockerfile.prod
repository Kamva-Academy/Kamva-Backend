# pull official base image
FROM python:3.7.4-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

# install python-dev
RUN apk update \
    && apk add --virtual .build-deps gcc libc-dev libxslt-dev \
    && apk add libffi-dev openssl-dev linux-headers \
    && apk add --no-cache libxslt \
    && pip install lxml==4.5.0

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && pip install --upgrade incremental

# install zlib for pillow
RUN apk add --no-cache g++ freetype-dev jpeg-dev zlib-dev build-base

# install dependencies
RUN pip install --upgrade pip setuptools

# copy requirements
COPY requirements.txt /usr/src/requirements.txt

RUN pip install -r /usr/src/requirements.txt

# TODO: move it to requirements
RUN pip install django-cors-headers==3.4.0

# copy entrypoint-prod.sh
COPY ./entrypoint.prod.sh /usr/src/app/entrypoint.prod.sh

# copy project
COPY . /usr/src/app/

RUN adduser -D workshop

RUN mkdir -p /usr/src/app/logging && chown -R workshop /usr/src/app/logging \
	&& mkdir -p /usr/src/app/staticfiles && chown -R workshop /usr/src/app/staticfiles \
	&& mkdir -p /usr/src/app/media && chown -R workshop /usr/src/app/media

RUN chown -R workshop /usr/src/app/

USER workshop

# run entrypoint.prod.sh
ENTRYPOINT ["/usr/src/app/entrypoint.prod.sh"]
