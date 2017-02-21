#!/usr/bin/env python
# coding: utf-8

'''
email notifier
--------------
'''
__author__ = "François Gouteroux <francois.gouteroux@gmail.com>"

import smtplib
import email.utils
from email.mime.text import MIMEText
from flask import current_app as app

def send(notifier, data):
    """Send email notification

    Args:
        notifier (dict): email properties
        data (dict): data

    Returns:
        n/a: This function had no return.

    Raises:
        n/a: This function didn't raise.

    Usage:
        >>> send(notifier, data)
    """
    if isinstance(data, list):
        msg = MIMEText("\n".join(data))
    else:
        msg = MIMEText(str(data))

    msg['To'] = notifier["to"]
    msg['From'] = email.utils.formataddr(('Platus', notifier["fr"]))

    msg['Subject'] = notifier["subject"]

    server = smtplib.SMTP(notifier["host"])
    try:
        server.set_debuglevel(False)
        server.ehlo()

        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()

        if notifier.get("username") is not None and notifier.get("password") is not None:
            server.login(notifier["username"], notifier["password"])

        server.sendmail(notifier["fr"], [notifier["to"]], msg.as_string())
        app.logger.debug("Email - Success")

    except smtplib.SMTPException as error_msg:
        app.logger.error("Email - Error: {0}".format(error_msg))

    finally:
        server.quit()
