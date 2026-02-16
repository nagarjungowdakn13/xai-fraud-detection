from flask import Flask
from flask_cors import CORS
import importlib
import logging

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Optional blueprints: import and register if present
    blueprints = {
        'app.auth': ('auth_bp', '/auth'),
        'app.fraud': ('fraud_bp', '/fraud'),
        'app.models': ('models_bp', '/models'),
        'app.recommendations': ('recommendations_bp', '/recommendations'),
        'app.graph': ('graph_bp', '/graph'),
    }

    for module_name, (bp_name, prefix) in blueprints.items():
        try:
            module = importlib.import_module(module_name)
            bp = getattr(module, bp_name)
            app.register_blueprint(bp, url_prefix=prefix)
        except Exception as e:
            # Blueprint missing or failed to import; skip gracefully
            print(f"Error loading blueprint {module_name}: {e}")
            logger.debug(f"Skipping blueprint {module_name}.{bp_name}")

    return app
