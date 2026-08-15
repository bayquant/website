# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Standard library imports
import logging
import tarfile
import urllib.error
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI

# Local imports
from .brain_content import load_brain_content
from .routers import bay_quant, brain

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["app"]

_logger = logging.getLogger("uvicorn.error")

# -----------------------------------------------------------------------------
# General API
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pull the bayquant/brain notes once at startup. A GitHub hiccup must not
    # crash the app, so on failure the /brain routes degrade to an empty state.
    try:
        app.state.brain_notes, app.state.brain_css = load_brain_content()
        _logger.info("Loaded %d notes from bayquant/brain", len(app.state.brain_notes))
    except (urllib.error.URLError, tarfile.TarError, TimeoutError) as exc:
        _logger.warning("Failed to fetch bayquant/brain notes: %s", exc)
        app.state.brain_notes, app.state.brain_css = {}, ""
    yield


app = FastAPI(title="BayQuant", lifespan=lifespan)

app.include_router(bay_quant.router)
app.include_router(brain.router)
