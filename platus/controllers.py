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
from deepdiff import DeepDiff

def services_status(roles):
    """Check services health"""

    log = app.logger
    services_states = []

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
                log.error("Unable to get service status. Reason: %s" % error)

    if services_states:
        if app.config['notify']:

            if app.config['persistent_data'] and app.config['persistent_data_backend']:

                storage_backend = app.config['persistent_data_backend']["type"]
                log.debug("Try importing persistent data backend %s" % storage_backend)
                call_storage_bd = importlib.import_module("platus.storage.{0}_backend"\
                                                          .format(storage_backend))

                client = call_storage_bd.login(**app.config['persistent_data_backend']['data'])

                last_service_states = []
                for service in services_states:

                    last_service = call_storage_bd.get_service_status(client, service["name"])
                    call_storage_bd.set_service_status(client, service)

                    last_service_states.append(last_service)

                diff = DeepDiff(last_service_states, services_states, ignore_order=True)
                new_states = diff.get("iterable_item_added")
                old_states = diff.get("iterable_item_removed")

                if new_states is not None and old_states is not None:
                    report_changes = []
                    for k, v in six.iteritems(new_states):
                        if v["state"] != old_states[k]["state"]:
                            changed = "{0} state changed to {1} before it was {2}"\
                                      .format(v["name"],
                                              v["state"],
                                              old_states[k]["state"])
                            log.debug(changed)
                            report_changes.append(changed)

                    if report_changes:
                        log.debug("Some services status changed.")
                        log.debug(report_changes)
                        notify_backend = app.config['notify_backend']["type"]
                        log.debug("Try importing notify backend %s" % notify_backend)
                        call_notify_bd = importlib.import_module("platus.notifier.{0}_backend"\
                                                                  .format(notify_backend))

                        call_notify_bd.send(app.config['notify_backend']['data'], report_changes)

        return sorted(services_states, key=lambda plug: plug['type'])
    else:
        return ["No data"]
