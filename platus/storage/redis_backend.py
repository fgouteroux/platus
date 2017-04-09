#!/usr/bin/env python
# coding: utf-8
'''
redis store
--------------
'''
import redis

# Import third party libs
from flask import current_app as app

def login(**kwargs):
    return redis.Redis(**kwargs)

def set_service_status(client, data):
    """Store service status

    Args:
        client (Client): client connection object
        data (dict): service data

    Returns:
        n/a: This function had no return.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> set_service_status(client, service)
    """
    service_name = data["name"]
    client.hmset(service_name, data)

    app.logger.debug("redis - set {0}: {1}".format(service_name, data))


def get_service_status(client, service_name):
    """Get service status

    Args:
        client (Client): client connection object
        service_name (str): service name to get

    Returns:
        dict: service status.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> get_service_status(client, service_name)
    """
    data = client.hgetall(service_name)
    app.logger.debug("redis - get {0}: {1}".format(service_name, data))
    return data


def flush(client):
    """flush db

    Args:
        client (Client): client connection object

    Returns:
        bool: True if success.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> flushdb(client)
    """
    result = client.flushdb()
    app.logger.debug("redis - flush db: {0}".format(result))
    return result
