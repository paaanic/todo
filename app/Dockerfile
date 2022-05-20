FROM python:3.10.4-bullseye

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/requirements.txt

RUN apt-get update \
    && apt-get install libcairo-dev \
    && pip install --upgrade pip \
    && pip install -r /usr/src/requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /usr/src/app/
