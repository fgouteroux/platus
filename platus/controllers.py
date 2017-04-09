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

def _get_storage_module():
    """Return storage client"""
    storage_backend = app.config['persistent_data_backend']["type"]
    app.logger.debug("Try importing persistent data backend %s" % storage_backend)
    return importlib.import_module("platus.storage.{0}_backend"\
                                              .format(storage_backend))


def _get_vault_secret(vault_client, vault_call, properties):
    """search and get vault secret"""
    for key in properties.keys():
        if key.startswith("vault_"):
            value = vault_call.read_vault_secret(\
                        vault_client,
                        properties[key])

            unvault_key = key.split("vault_")[1]
            properties[unvault_key] = value
            properties.pop(key)


def _notify(services_states):
    """Notify services health"""
    call_storage_bd = _get_storage_module()
    client = call_storage_bd.login(**app.config['persistent_data_backend']['data'])

    report_changes = []
    retry_limit = app.config.get('retries_before_notify', 3)

    for service in services_states:
        last_service = call_storage_bd.get_service_status(client, service["name"])
        app.logger.debug(last_service)

        if last_service:

            if service["state"] != last_service["state"] and service["state"] == "operational":
                # Reset counter and last state
                service["retries"] = 0
                service["last_state"] = "operational"
                changed = "{0} state changed to {1} before it was {2}"\
                          .format(service["name"],
                                  service["state"],
                                  last_service["state"])

                report_changes.append(changed)

            elif service["state"] == last_service["state"] and service["state"] == "operational":
                # Reset counter and last state
                service["retries"] = 0
                service["last_state"] = "operational"
            else:
                service["last_state"] = last_service["last_state"]
                changed = "{0} state changed to {1} before it was {2}"\
                          .format(service["name"],
                                  service["state"],
                                  service["last_state"])
                service["retries"] = int(last_service.get("retries", 0)) + 1

                if service["retries"] == retry_limit:
                    report_changes.append(changed)

        # Get values or init if not found
        service["retries"] = service.get("retries", 0)
        service["last_state"] = service.get("last_state", service["state"])

        # Update service status
        call_storage_bd.set_service_status(client, service)

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

    vault = app.config.get("vault", False)
    if vault:
        vault_call = importlib.import_module("platus.vault")
        vault_client = vault_call.login(**app.config["vault_backend"])

    for name, service in six.iteritems(get_services):

        if "admin" in roles or (set(roles) & set(service["role"])):
            plugin = service["type"]

            try:
                app.logger.debug("Read service %s" % name)
                app.logger.debug("Try importing plugin %s" % plugin)
                call_service = importlib.import_module("platus.plugins.{0}"\
                                                      .format(plugin))

                if vault:
                    _get_vault_secret(vault_client, vault_call, service["properties"])

                client = call_service.login(**service["properties"])
                status = call_service.check_health(client, service["data"])

                app.logger.debug("service status: %s" % status)

                if isinstance(status, list):
                    for i in status:
                        services_states.append(i)
                else:
                    services_states.append(status)

            except RuntimeError as error:
                host = service["properties"]['host']
                if isinstance(host, list):
                    for item in host:
                        status = {"type": service["data"]["type"],
                                  "name": service["data"]["name"],
                                  "node": item,
                                  "state": "down",
                                  "checked": str(datetime.now()),
                                  "retries": service.get("retries", 0)
                                 }
                else:
                    status = {"type": service["data"]["type"],
                              "name": service["data"]["name"],
                              "node": host,
                              "state": "down",
                              "checked": str(datetime.now()),
                              "retries": service.get("retries", 0)
                             }

                services_states.append(status)
                app.logger.error("Unable to get service status. Reason: %s" % error)

    if services_states:

        if app.config['notify'] and app.config['persistent_data']\
        and app.config['persistent_data_backend']:
            _notify(services_states)

        return sorted(services_states, key=lambda plug: plug['type'])
    else:
        return ["No data"]

def flush_data():
    """Flush services status data"""
    if app.config['persistent_data'] and app.config['persistent_data_backend']:
        storage_backend = _get_storage_module()
        client = storage_backend.login(**app.config['persistent_data_backend']['data'])
        return storage_backend.flush(client)
