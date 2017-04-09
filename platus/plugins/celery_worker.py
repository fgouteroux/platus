#!/usr/bin/env python
# coding: utf-8

'''
celery worker plugin
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
import six
import time
import atexit
from datetime import datetime, timedelta

# Import third party libs
from celery import Celery
from flask import current_app as app


def login(host, username, password, port=5672, transport="amqp"):
    """Login to celery

    Args:

        host (str): celery host
        username (str): celery username
        password (str): celery password
        port (Optional[int]): celery port
        transport (Optional[str]): celery transport

    Returns:
        Client: client connection object

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> login(host="mongode.lan",
                  transport="amqp",
                  port="27017")
    """
    broker_url = "{0}://{1}:{2}@{3}:{4}/{5}".format(transport,
                                                    username,
                                                    password,
                                                    host,
                                                    port,
                                                    host)
    client = Celery('status', broker=broker_url)

    atexit.register(logout, client)
    return client


def logout(client):
    """Close the connection to the server

    Args:
        client (Client): client connection object

    Returns:
        n/a: This function had no return.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> logout(client)
    """
    if isinstance(client, Celery):
        client.close()


def check_health(client, data):
    """Check celery plugin health

    Args:
        client (Client): client connection object
        data (dict): data

    Returns:
        workers (list): dict of workers status

    Raises:
        RuntimeError: Unable to check celery plugin health.

    Usage:
        >>> check_health(client, data)
    """
    try:
        start_time = time.time()
        workers_state = client.control.inspect().ping()
        elapsed_time = timedelta(seconds=(time.time() - start_time))

        app.logger.debug("celery_worker - response: {0}".format(workers_state))

        workers = []
        for worker, result in six.iteritems(workers_state):

            state = result['ok']

            if state == "pong":
                status = {"type": data["type"],
                          "name": data["name"],
                          "node": worker,
                          "state": "operational",
                          "checked": str(datetime.now()),
                          "elapsed": str(elapsed_time)
                         }
            else:
                status = {"type": data["type"],
                          "name": data["name"],
                          "node": worker,
                          "state": "down",
                          "checked": str(datetime.now()),
                          "elapsed": str(elapsed_time)
                         }
            workers.append(status)

        if workers:
            return workers

    except Exception as error_msg:
        app.logger.error("celery_worker - {0} => {1}".format(data["name"], error_msg))

        return {"type": data["type"],
                "name": data["name"],
                "node": client.host,
                "state": "unknown",
                "checked": str(datetime.now())
               }
