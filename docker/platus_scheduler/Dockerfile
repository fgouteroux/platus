FROM python:2.7
MAINTAINER François Gouteroux <francois.gouteroux@gmail.com>

ADD platus_scheduler.py  /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD celery worker -B -l info -A platus_scheduler.app