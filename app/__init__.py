from flask import Flask

from app.database import db
from app.blueprints import bp


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='secret')
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

    app.register_blueprint(bp)

    return app
