# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# Third-party imports
from fastapi import APIRouter

# Local imports
from . import health

# -----------------------------------------------------------------------------
# Globals and constants
# -----------------------------------------------------------------------------
__all__ = ["router"]

# JSON endpoints. Listed in the OpenAPI schema.
router = APIRouter(tags=["api"])
router.include_router(health.router)
