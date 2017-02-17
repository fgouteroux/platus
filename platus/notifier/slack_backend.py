#!/usr/bin/env python
# coding: utf-8

'''
slack notifier
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

# Import third party libs
import requests
from flask import current_app as app

def send(notifier, data):
    """Send slack notification

    Args:
        web_hook_url (str): web hook_url of slack
        data (dict): data

    Returns:
        n/a: This function had no return.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> send(web_hook_url, data)
    """
    try:
        web_hook_url = notifier.get('url')

        if not web_hook_url:
            app.logger.error("slack - Error: Url not found or empty in notifier data. "\
                             "Getting {0}".format(notifier))
        else:
            if isinstance(data, list):
                payload = {"text": "\n".join(data)}
            else:
                payload = {"text": str(data)}

            response = requests.post(web_hook_url, json=payload)

            if response.status_code == 200:
                app.logger.debug("slack - status code: {0} => {1}"\
                                 .format(response.status_code, response.text))
            else:
                app.logger.error("slack - status code: {0} => {1}"\
                                 .format(response.status_code, response.text))


    except Exception as error_msg:
        app.logger.error("slack - Error: {0}".format(error_msg))
