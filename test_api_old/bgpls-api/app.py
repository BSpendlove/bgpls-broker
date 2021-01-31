from config import Config
from flask import Flask
from flask_migrate import Migrate
import logging

# App Config
app = Flask(__name__)
app.config.from_object(Config)

# Logging
app.logger.setLevel(logging.DEBUG)

# Database Models
from models import db
migrate = Migrate(app, db)

# Views
from views import test_views
from views.exabgp.neighbor import state

db.init_app(app)
db.create_all()

if __name__ == "__main__":
    app.register_blueprint(test_views.bp)
    app.register_blueprint(state.bp)
    app.run(host="0.0.0.0", port=5000, debug=True)