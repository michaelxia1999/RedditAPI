from fastapi import Request
from fastapi.exceptions import RequestValidationError


async def handle_request_validation_error(request: Request, e: RequestValidationError):
    # route back to exception_handlder_middleware
    raise e