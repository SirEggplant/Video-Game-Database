
"""Video Game Database backend package."""

# Legacy feature modules import ``src`` as a top-level package.  Registering
# this alias keeps those imports working when the API is started with
# ``uvicorn backend.api:app``.
import sys

from . import src as _src

sys.modules.setdefault("src", _src)
