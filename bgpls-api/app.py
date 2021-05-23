from flask import Flask
import env_file
import logging

# App Config
app = Flask(__name__)

# Logging
app.logger.setLevel(logging.DEBUG)

# Views
from views.api import api_mongodb
from views.api import api

if __name__ == "__main__":
    app.register_blueprint(api.bp)
    app.register_blueprint(api_mongodb.bp)
    app.run(host="0.0.0.0", port=5000, debug=True)
