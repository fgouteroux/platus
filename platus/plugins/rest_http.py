#!/usr/bin/env python
# coding: utf-8

'''
rest http plugin
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
import atexit
import tempfile
from datetime import datetime
from collections import namedtuple

# Import third party libs
import requests
from flask import current_app as app
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Client = namedtuple('Client',
                    ['host', 'conn', 'base_url', 'key_file', 'cert_file'])

def login(host, protocol="https", port=443, **kwargs):
    """Login to the rest http plugin

    Args:

        host (str): rest http host
        protocol (Optional[str]): rest http protocol
        port (Optional[int]): rest http port

    Kwargs:
        token (str): rest http token
        username (str): rest http username
        password (str): rest http password
        cert (str): rest http certificate
        key (str): rest http keyfile

    Returns:
        Client: client connection object

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> login(host="rest_http.lan",
                  protocol="http",
                  port="8080")
    """
    base_url = "{protocol}://{host}:{port}"\
                .format(protocol=protocol,
                        host=host,
                        port=int(port))
    # create session
    conn = requests.Session()
    if "username" and "password" in kwargs:
        conn.auth = (kwargs["username"], kwargs["password"])

    if "request_format" in kwargs:
        conn.headers = {
            "Content-Type": kwargs["request_format"],
            "Accept": kwargs["request_format"],
        }
    else:
        conn.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    if "token" in kwargs:
        conn.headers["PRIVATE-TOKEN"] = kwargs["token"]

    if "cert" and "key" in kwargs:
        key_file = tempfile.NamedTemporaryFile()
        cert_file = tempfile.NamedTemporaryFile()

        # Auth with certificate and key file
        key_file.write(kwargs["key"])
        key_file.seek(0)
        cert_file.write(kwargs["cert"])
        cert_file.seek(0)
        conn.cert = (cert_file.name, key_file.name)
    else:
        key_file = None
        cert_file = None

    conn.verify = False

    client = Client(host=host, base_url=base_url, conn=conn,
                    key_file=key_file, cert_file=cert_file)
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
        if client.conn:
            client.conn.close()


def check_health(client, data):
    """Check rest http plugin health

    Args:
        client (Client): client connection object
        data (dict): data

    Returns:
        status (dict): Rest http plugin status.

    Raises:
        RuntimeError: Unable to check rest http plugin health.

    Usage:
        >>> check_health(client, data)
    """
    url = client.base_url + data["url"]

    try:
        response = client.conn.get(url)
        status = None

        app.logger.debug("rest_http - status code: {0} => {1}"\
                  .format(response.status_code, response.text))

        if response.status_code == 200:
            status = {"type": data["type"],
                      "name": data["name"],
                      "node": client.host,
                      "state": "operational",
                      "checked": str(datetime.now()),
                      "elapsed": str(response.elapsed)
                     }
            if data.get("search"):
                search = data["search"]
                if isinstance(search, str) and search not in response.text:
                    status["state"] = "unhealthy"
                elif isinstance(search, dict):
                    result = response.json()
                    if not search.viewitems() <= result.viewitems():
                        status["state"] = "unhealthy"

        else:
            status = {"type": data["type"],
                      "name": data["name"],
                      "node": client.host,
                      "state": "down",
                      "checked": str(datetime.now()),
                      "elapsed": str(response.elapsed)
                     }
        if status:
            return status

    except Exception as error_msg:
        app.logger.error("rest_http - {0} => {1}".format(data["name"], error_msg))

        return {"type": data["type"],
                "name": data["name"],
                "node": client.host,
                "state": "down",
                "checked": str(datetime.now())
               }
