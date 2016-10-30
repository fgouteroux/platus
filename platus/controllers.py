#!/usr/bin/env python
# coding: utf-8
'''
platus controllers
--------------
'''
from __future__ import absolute_import

__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import Python libs
import six
import yaml
import importlib
from datetime import datetime

# Import third party libs
from flask import current_app as app

def services_status(roles):
    """Check services health"""

    log = app.logger
    p_status = []

    try:
        with open(app.config['services'], 'r') as content:
            get_services = yaml.load(content)
    except IOError:
        message = "Config file not found for services"
        log.error(message)
        return [message]

    for name, service in six.iteritems(get_services):

        if "admin" in roles or (set(roles) & set(service["role"])):
            plugin = service["type"]

            try:
                log.debug("Read service %s" % name)
                log.debug("Try importing plugin %s" % plugin)
                call_service = importlib.import_module("platus.plugins.{0}"\
                                                      .format(plugin))

                client = call_service.login(**service["properties"])
                status = call_service.check_health(client, service["data"])

                log.debug("service status: %s" % status)

                if isinstance(status, list):
                    for i in status:
                        p_status.append(i)
                else:
                    p_status.append(status)

            except RuntimeError, error:
                host = service["properties"]['host']
                if isinstance(host, list):
                    for item in host:
                        status = {"type": service["data"]["type"],
                                  "name": service["data"]["name"],
                                  "node": item,
                                  "state": "down",
                                  "checked": str(datetime.now())
                                 }
                else:
                    status = {"type": service["data"]["type"],
                              "name": service["data"]["name"],
                              "node": host,
                              "state": "down",
                              "checked": str(datetime.now())
                             }

                p_status.append(status)
                log.error("Unable to get service status. Reason: %s" % error)

    if p_status:
        return sorted(p_status, key=lambda plug: plug['type'])
    else:
        return ["No data"]
