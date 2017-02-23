#!/usr/bin/env python
# coding: utf-8

'''
vault plugin
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
import six
import yaml
import json
import atexit
import tempfile
from collections import namedtuple

# Import third party libs
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Client = namedtuple('Client',
                    ['host', 'conn', 'base_url', 'key_file', 'cert_file'])

def login(host="localhost", protocol="http", port=8200, path="/v1/secret/", **kwargs):
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
    base_url = "{protocol}://{host}:{port}/{path}"\
                .format(protocol=protocol,
                        host=host,
                        port=int(port),
                        path=path)
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
        conn.headers["X-Vault-Token"] = kwargs["token"]

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
    """Close the connection to the server"""
    if isinstance(client, Client):
        if client.conn:
            client.conn.close()

def write_vault_secret(client, vault_key, vault_secret):
    """Get password from vault"""

    url = client.base_url + vault_key
    data = {"value": vault_secret}

    response = client.conn.post(url, data=json.dumps(data))

    if response.status_code == 204:
        return True


def read_vault_secret(client, vault_key):
    """Get password from vault"""

    url = client.base_url + vault_key

    response = client.conn.get(url)
    content = response.json()
    # {u'lease_id': u'', u'warnings': None, u'auth': None, u'lease_duration': 2592000,
    # u'data': {u'value': u'7175b4cfff396de2c136d052bfac6b0d4'}, u'renewable': False}

    if response.status_code == 200:
        return content.get('data', {}).get('value', "")

def get_secrets_from_file(path):
    """Get secrets from yaml file"""
    try:
        with open(path, 'r') as content:
            secrets = yaml.load(content)
            if secrets is None:
                return "Secrets file empty"
            return secrets
    except IOError:
        return "Secrets file not found."

if __name__ == '__main__':
    path = "vault_secrets.yml"
    secrets = get_secrets_from_file(path)

    client = login(
                host="localhost",
                port=8200,
                protocol="http",
                token="b4169582-e3d1-b752-64e7-d3ad453a67eb",
                path="/v1/secret/")

    for key, secret in six.iteritems(secrets):
        print "write secret:", key
        write_vault_secret(client, key, secret)
        #print "read secret", read_vault_secret(client, key)

