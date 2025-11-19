"""Runtime checker for the backend app.

This script patches `pkgutil.get_loader` if missing (Python 3.14+),
loads `backend/app/app_factory.py` by path to avoid importing the package
`backend.app` (which may have broken __init__), and prints registered routes.
"""
import sys
import pkgutil
import importlib.util
import importlib
import os

# Add project root to sys.path so 'backend' package can be imported
HERE = os.path.dirname(__file__) or '.'
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Patch pkgutil.get_loader for compatibility with older libraries
if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        spec = importlib.util.find_spec(name)
        return spec.loader if spec is not None else None
    pkgutil.get_loader = _get_loader

APP_FACTORY_PATH = os.path.join(HERE, '..', 'backend', 'app', 'app_factory.py')
APP_FACTORY_PATH = os.path.abspath(APP_FACTORY_PATH)

spec = importlib.util.spec_from_file_location('app_factory', APP_FACTORY_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

app = mod.create_app()
print('ROUTES:', [r.rule for r in app.url_map.iter_rules()])
