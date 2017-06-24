# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_assets import Environment, Bundle

import logging
from logging.handlers import RotatingFileHandler

from platus.web import web
from platus.api import api
from platus.config import config


application = Flask(__name__,\
                    static_folder="platus/static/",\
                     template_folder="platus/templates/",
                    static_url_path="/static")
application.register_blueprint(web)
application.register_blueprint(api)

application.config.update(config.from_yaml("data/config.yaml"))

# Scss
assets = Environment(application)
assets.versions = 'timestamp'
assets.url_expire = True
assets.manifest = 'file:/tmp/manifest.to-be-deployed'  # explict filename
assets.cache = False
assets.auto_build = True

assets.url = application.static_url_path
scss = Bundle('scss/00_main.scss', filters='pyscss', output='css/main.css',  depends=['scss/*.scss'])
assets.register('scss_all', scss)

assets.debug = False
application.config['ASSETS_DEBUG'] = False

# Set Logger
log_levels = {
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

log_level = log_levels[application.config.get("log_level", "info")]


log = logging.getLogger(__name__)
console_formatter = logging.Formatter(
            '%(levelname)s\t%(filename)s:%(lineno)d\t\t%(message)s', '%m-%d %H:%M:%S')
file_formatter = logging.Formatter(
            '%(levelname)s - %(asctime)s - %(pathname)s - %(lineno)d - %(message)s', '%m-%d %H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(console_formatter)

rotatingfile_handler = RotatingFileHandler('platus.log', maxBytes=10000, backupCount=1)
rotatingfile_handler.setLevel(log_level)
rotatingfile_handler.setFormatter(file_formatter)

application.logger.addHandler(console_handler)
application.logger.addHandler(rotatingfile_handler)
application.logger.setLevel(log_level)

if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5001)
