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

def notify(services_states):
    """Notify services health"""
    storage_backend = app.config['persistent_data_backend']["type"]
    app.logger.debug("Try importing persistent data backend %s" % storage_backend)
    call_storage_bd = importlib.import_module("platus.storage.{0}_backend"\
                                              .format(storage_backend))

    client = call_storage_bd.login(**app.config['persistent_data_backend']['data'])

    report_changes = []

    for service in services_states:

        last_service = call_storage_bd.get_service_status(client, service["name"])
        call_storage_bd.set_service_status(client, service)

        if service["state"] != last_service["state"]:
            changed = "{0} state changed to {1} before it was {2}"\
                          .format(service["name"],
                                  service["state"],
                                  last_service["state"])

            app.logger.debug(changed)
            report_changes.append(changed)

    if report_changes:
        app.logger.debug("Some services status changed.")
        app.logger.debug(report_changes)
        notify_backend = app.config['notify_backend']["type"]
        app.logger.debug("Try importing notify backend %s" % notify_backend)
        call_notify_bd = importlib.import_module("platus.notifier.{0}_backend"\
                                                  .format(notify_backend))

        call_notify_bd.send(app.config['notify_backend']['data'], report_changes)

def services_status(roles):
    """Check services health"""
    services_states = []

    try:
        with open(app.config['services'], 'r') as content:
            get_services = yaml.load(content)
    except IOError:
        message = "Config file not found for services"
        app.logger.error(message)
        return [message]

    for name, service in six.iteritems(get_services):

        if "admin" in roles or (set(roles) & set(service["role"])):
            plugin = service["type"]

            try:
                app.logger.debug("Read service %s" % name)
                app.logger.debug("Try importing plugin %s" % plugin)
                call_service = importlib.import_module("platus.plugins.{0}"\
                                                      .format(plugin))

                client = call_service.login(**service["properties"])
                status = call_service.check_health(client, service["data"])

                app.logger.debug("service status: %s" % status)

                if isinstance(status, list):
                    for i in status:
                        services_states.append(i)
                else:
                    services_states.append(status)

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

                services_states.append(status)
                app.logger.error("Unable to get service status. Reason: %s" % error)

    if services_states:

        if app.config['notify'] and app.config['persistent_data']\
        and app.config['persistent_data_backend']:
            notify(services_states)

        return sorted(services_states, key=lambda plug: plug['type'])
    else:
        return ["No data"]
