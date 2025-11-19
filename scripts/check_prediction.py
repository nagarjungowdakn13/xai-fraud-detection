"""Check import/startup for prediction-api/run.py with Python 3.14 compat patches."""
import pkgutil
import importlib.util
import importlib
import os

# Patch missing attributes for compatibility with some packaging code
if not hasattr(pkgutil, 'get_loader'):
    def _get_loader(name):
        spec = importlib.util.find_spec(name)
        return spec.loader if spec is not None else None
    pkgutil.get_loader = _get_loader

if not hasattr(pkgutil, 'ImpImporter'):
    # Some older tooling checks for ImpImporter; provide a stub
    pkgutil.ImpImporter = None

spec = importlib.util.spec_from_file_location('pred_run', os.path.abspath(os.path.join('prediction-api', 'run.py')))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('prediction-api imported successfully')
