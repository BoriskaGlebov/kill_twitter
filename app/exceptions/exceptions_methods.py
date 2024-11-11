from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Обработка исключений HTTPException.

    :param request: Запрос, вызвавший исключение.
    :param exc: Исключение HTTPException.
    :return: JSONResponse с информацией об ошибке.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": False, "error_type": "HTTPException", "error_message": exc.detail},
    )


async def integrity_error_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Обработка исключений IntegrityError.

    :param request: Запрос, вызвавший исключение.
    :param exc: Исключение IntegrityError.
    :return: JSONResponse с информацией об ошибке.
    """
    return JSONResponse(
        status_code=409,
        content={"result": False, "error_type": "sqlalchemy.exc.IntegrityError", "error_message": repr(exc.orig)},
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Обработка исключений ValidationError.

    :param request: Запрос, вызвавший исключение.
    :param exc: Исключение ValidationError.
    :return: JSONResponse с информацией об ошибке.
    """
    return JSONResponse(
        status_code=400, content={"result": False, "error_type": "Validation error", "error_message": exc.errors()}
    )
