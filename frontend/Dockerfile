FROM python:3.9

LABEL maintainer="404"
LABEL name = "Prykhodzka lerans ho to web"

WORKDIR /app
ARG requirements=requirements/production.txt

ADD . /app

RUN pip install --no-cache-dir -r $requirements
RUN pip install --no-cache-dir -e .
