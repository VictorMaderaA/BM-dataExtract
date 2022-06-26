# Here is the build image
FROM python:3.8.0-slim as builder

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN apt-get install gcc libpq-dev -y
RUN apt-get install python-dev  python-pip -y
RUN apt-get install python3-dev python3-pip python3-venv python3-wheel -y
RUN apt-get install build-essential libssl-dev libffi-dev python-dev libffi-dev -y
RUN apt-get install mariadb-client -y
RUN pip3 install wheel

RUN pip3 install setuptools wheel


WORKDIR app

COPY requirements.txt .

RUN pip3 install --user -r requirements.txt

ENV PATH=/root/.local/bin:$PATH
ENV TZ=Europe/Madrid

COPY . /app

ENTRYPOINT ['python']

