# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_assets import Environment, Bundle

# change it
from platus.web import web
from platus.api import api

import logging
from logging.handlers import RotatingFileHandler

application = Flask(__name__,\
                    static_folder="platus/static/",\
                     template_folder="platus/templates/",
                    static_url_path="/static")
application.register_blueprint(web)
application.register_blueprint(api)

application.config['services'] = "services.yaml"
application.config['users'] = "users.yaml"

application.config['persistent_data'] = True
application.config['persistent_data_backend'] = {"type": "redis",
                                                 "data": {"host":"127.0.0.1"}
                                                }

application.config['notify'] = True
application.config['notify_backend'] = {"type": "slack",
                                        "data": {
                                            "url": ""
                                            }
                                       }

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
log = logging.getLogger(__name__)
console_formatter = logging.Formatter(
            '%(levelname)s\t%(filename)s:%(lineno)d\t\t%(message)s', '%m-%d %H:%M:%S')
file_formatter = logging.Formatter(
            '%(levelname)s - %(asctime)s - %(pathname)s - %(lineno)d - %(message)s', '%m-%d %H:%M:%S')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)

rotatingfile_handler = RotatingFileHandler('platus.log', maxBytes=10000, backupCount=1)
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(file_formatter)

log.addHandler(console_handler)
log.addHandler(rotatingfile_handler)
log.setLevel(logging.DEBUG)



def run():
    # Start Application
    log.info("start application")
    application.run(host="0.0.0.0", debug=False, port=5001, threaded=True)


if __name__ == '__main__':
    run()
