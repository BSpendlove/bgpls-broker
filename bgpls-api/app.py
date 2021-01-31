from flask import Flask
import logging

# App Config
app = Flask(__name__)

# Logging
app.logger.setLevel(logging.DEBUG)

# Views
from views.exabgp.neighbor import state

if __name__ == "__main__":
    app.register_blueprint(state.bp)
    app.run(host="0.0.0.0", port=5000, debug=True)