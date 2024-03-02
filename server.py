#!python

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_cors import CORS

from jmon.api import FlaskApp
import jmon.config


flask_app = FlaskApp()

if jmon.config.Config.get().SENTRY_DSN:
    sentry_sdk.init(
        dsn=jmon.config.Config.get().SENTRY_DSN,
        enable_tracing=True,
        integrations = [
            FlaskIntegration(
                transaction_style="url",
            ),
        ],
        environment=jmon.config.Config.get().SENTRY_ENVIRONMENT,
    )

CORS(flask_app.app)
flask_app.app.run(host='0.0.0.0', threaded=True)