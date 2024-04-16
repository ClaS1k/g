from fastapi import APIRouter

from app.endpoints.auth import router as auth_router
from app.endpoints.other import router as other_router


router = APIRouter(
    prefix="/api",
    responses={404: {"description": "biome api"}},
)

router.include_router(auth_router)
router.include_router(other_router)

