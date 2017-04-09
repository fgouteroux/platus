#!/usr/bin/env python
# coding: utf-8

'''
mongodb plugin
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
import ssl
import time
import atexit
from collections import namedtuple
from datetime import datetime, timedelta

# Import third party libs
from pymongo import MongoClient
from flask import current_app as app

Client = namedtuple('Client', ['host'])

def login(host, username, password, port=27017, protocol="mongodb"):
    """Login to mongodb

    Args:

        host (str): mongodb host
        username (str): mongodb username
        password (str): mongodb password
        port (Optional[int]): mongodb port
        protocol (Optional[str]): mongodb protocol

    Returns:
        Client: client connection object

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> login(host="mongode.lan",
                  protocol="mongodb",
                  port="27017")
    """
    if isinstance(host, list):
        conn = []
        for item in host:
            base_url = "{protocol}://{host}:{port}".format(protocol=protocol,
                                                           host=item,
                                                           port=int(port))
            conn.append(base_url)
        client = MongoClient(conn, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
    else:
        base_url = "{protocol}://{host}:{port}"\
                .format(protocol=protocol,
                        host=host,
                        port=int(port))
        client = MongoClient(base_url, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)


    is_logged = client.admin.authenticate(username, password)
    app.logger.debug("mongodb - is_logged: {0}".format(is_logged))

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
    if isinstance(client, Client):
        client.close()


def check_health(client, data):
    """Check mongodb state

    Args:
        client (Client): client connection object
        data (dict): data

    Returns:
        members_state (list): dict of members status

    Raises:
        RuntimeError: Unable to check mongodb plugin health.

    Usage:
        >>> check_health(client, data)
    """
    try:
        start_time = time.time()

        # The replSetGetStatus command returns the status of the
        # replica set from the point of view of the current server
        # https://docs.mongodb.com/manual/reference/command/replSetGetStatus/
        rs_state = client.admin.command('replSetGetStatus')
        app.logger.debug("mongodb - response: {0}".format(rs_state))

        elapsed_time = timedelta(seconds=(time.time() - start_time))

        members_state = []
        for member in rs_state['members']:

            health = member['health']
            node = member['name'].split(':')[0]

            if health == 1:
                status = {"type": data["type"],
                          "name": data["name"],
                          "node": node,
                          "state": "operational",
                          "checked": str(datetime.now()),
                          "elapsed": str(elapsed_time)
                         }
            elif health == 0:
                status = {"type": data["type"],
                          "name": data["name"],
                          "node": node,
                          "state": "down",
                          "checked": str(datetime.now()),
                          "elapsed": str(elapsed_time)
                         }
            members_state.append(status)

        if members_state:
            return members_state

    except Exception as error_msg:
        app.logger.error("mongodb - {0} => {1}".format(data["name"], error_msg))

        return {"type": data["type"],
                "name": data["name"],
                "node": client.host,
                "state": "unknown",
                "checked": str(datetime.now())
               }
