from app.api.applications import router as applications_router
from app.api.profile import router as profile_router
from app.api.agent import router as agent_router

__all__ = ['applications_router', 'profile_router', 'agent_router']

