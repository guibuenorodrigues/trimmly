from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ExternalServiceError,
    ServiceError,
    ValidationError,
)
from app.lifespan import lifespan
from app.logger import configure_unified_logging, logger
from app.routers.router import set_routes

# Set up unified logging before creating the FastAPI app
configure_unified_logging()

app = FastAPI(title="Trimmly", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

set_routes(app)


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_exception_handler(request: Request, exc: EntityNotFoundError):
    """Handle EntityNotFoundError exceptions."""
    logger.warning(f"Entity not found: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "entity_name": exc.entity_name,
            "identifier": exc.identifier,
            "error_type": "entity_not_found",
        },
    )


@app.exception_handler(DuplicateEntityError)
async def duplicate_entity_exception_handler(request: Request, exc: DuplicateEntityError):
    """Handle DuplicateEntityError exceptions."""
    logger.warning(f"Duplicate entity: {exc}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": str(exc),
            "entity_name": exc.entity_name,
            "field_name": exc.field_name,
            "field_value": exc.field_value,
            "error_type": "duplicate_entity",
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_exception_handler(request: Request, exc: ValidationError):
    """Handle ValidationError exceptions."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "field_name": exc.field_name,
            "message": exc.message,
            "error_type": "validation_error",
        },
    )


@app.exception_handler(ServiceError)
async def service_error_exception_handler(request: Request, exc: ServiceError):
    """Handle ServiceError exceptions."""
    logger.error(f"Service error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": str(exc), "error_type": "service_error"}
    )


@app.exception_handler(ExternalServiceError)
async def external_service_error_exception_handler(request: Request, exc: ExternalServiceError):
    """Handle ExternalServiceError exceptions."""
    logger.error(f"External service error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "detail": str(exc),
            "service_name": exc.service_name,
            "message": exc.message,
            "error_type": "external_service_error",
        },
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"Value error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc), "error_type": "validation_error"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that catches all unhandled exceptions.
    This ensures no exception goes unhandled and provides consistent error responses.
    """
    # Log the full exception with traceback
    logger.error(
        f"Unhandled exception occurred: {type(exc).__name__}: {exc}",
        exc_info=True,
        extra={
            "request_method": request.method,
            "request_url": str(request.url),
            "exception_type": type(exc).__name__,
        },
    )

    # Determine if we're in development mode
    is_development = getattr(app, "debug", False) or getattr(app.state, "debug", False)

    # Prepare error response
    error_response = {
        "detail": "An internal server error occurred",
        "error_type": "internal_server_error",
        "request_id": id(request),  # Simple request ID for tracking
    }

    # Include debug information only in development
    if is_development:
        error_response.update(
            {
                "debug_info": {
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "request_method": request.method,
                    "request_path": request.url.path,
                }
            }
        )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)
