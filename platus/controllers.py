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


def plugins_status():
    """Check plugins health"""

    log = app.logger
    p_status = []

    try:
        with open(app.config['plugins'], 'r') as content:
            get_plugins = yaml.load(content)
    except IOError:
        message = "Config file not found for plugins"
        log.error(message)
        return [message]

    for name, plugin in six.iteritems(get_plugins):
        plugin_type = plugin["type"]

        try:
            log.debug("Read plugin %s" % name)
            log.debug("Try importing plugin %s" % plugin_type)
            call_plugin = importlib.import_module("platus.plugins.{0}"\
                                                  .format(plugin_type))
            client = call_plugin.login(**plugin["properties"])
            status = call_plugin.check_health(client, plugin["data"])

            log.debug("Plugin status: %s" % status)

            if isinstance(status, list):
                for i in status:
                    p_status.append(i)
            else:
                p_status.append(status)

        except RuntimeError, error:
            host = plugin["properties"]['host']
            if isinstance(host, list):
                for item in host:
                    status = {"type": plugin["data"]["type"],
                              "name": plugin["data"]["name"],
                              "node": item,
                              "state": "down",
                              "checked": str(datetime.now())
                             }
            else:
                status = {"type": plugin["data"]["type"],
                          "name": plugin["data"]["name"],
                          "node": host,
                          "state": "down",
                          "checked": str(datetime.now())
                         }

            p_status.append(status)
            log.error("Unable to get plugin status. Reason: %s" % error)

    if p_status:
        return sorted(p_status, key=lambda plug: plug['type'])
    else:
        return ["No data"]
