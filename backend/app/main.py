"""
Entry point for the LifeLine-ICT FastAPI application.

The application factory centralises configuration, router registration, and
exception handling. Using a factory enables future test suites and scripts to
instantiate isolated application instances while injecting database overrides.
"""

from fastapi import FastAPI

from .core.config import settings
from .core.logging import configure_logging
from .api import (
    errors,
    locations_router,
    maintenance_tickets_router,
    projects_router,
    resources_router,
    sensor_sites_router,
    analytics_router,
    alert_router,
    auth_router,
)


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.

    Returns
    -------
    FastAPI
        An application primed with global metadata and ready for router
        inclusion. Routers live under ``app.api`` and are registered during the
        bootstrapping phase inside this function once they are implemented.
    """

    configure_logging()

    app = FastAPI(
        title="LifeLine ICT Backend",
        description=(
            "CRUD APIs that manage campus ICT projects, assets, and support "
            "workflows for the Uganda University ICT initiative."
        ),
        version=settings.api_version,
        contact={
            "name": "LifeLine-ICT Core Team",
            "email": settings.contact_email,
        },
        license_info={
            "name": "MIT License",
            "identifier": "MIT",
        },
    )

    errors.register_exception_handlers(app)

    app.include_router(projects_router)
    app.include_router(resources_router)
    app.include_router(locations_router)
    app.include_router(maintenance_tickets_router)
    app.include_router(sensor_sites_router)
    app.include_router(analytics_router)
    app.include_router(alert_router)
    app.include_router(auth_router)

    @app.get("/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        """
        Provide a basic health indicator confirming application availability.

        Returns
        -------
        dict[str, str]
            JSON payload with a static status. The endpoint is intentionally
            lightweight to support campus monitoring systems and classroom
            demonstrations.
        """

        return {"status": "ok"}

    @app.get("/health/detailed", tags=["health"])
    async def detailed_healthcheck() -> dict:
        """
        Provide detailed health status including database connectivity.

        Returns
        -------
        dict
            Detailed health status including API, database, and timestamp.
        """
        from .core.database import engine
        from sqlalchemy import text

        db_status = "unhealthy"
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception:
            pass

        return {
            "status": "ok" if db_status == "healthy" else "degraded",
            "api": "healthy",
            "database": db_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }

    @app.get("/ready", tags=["health"])
    async def readiness() -> dict[str, str]:
        """
        Readiness probe for Kubernetes and container orchestration.

        Returns
        -------
        dict[str, str]
            JSON payload indicating if the service is ready to accept traffic.
        """
        return {"ready": "true"}

    return app


app = create_app()
