from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from .exceptions import BusinessError


def api_response(data=None, message="success", code=0, http_status=status.HTTP_200_OK):
    return Response({"code": code, "message": message, "data": data}, status=http_status)


def error_response(message, code=40000, http_status=status.HTTP_400_BAD_REQUEST, data=None):
    return api_response(data=data, message=message, code=code, http_status=http_status)


def business_error_response(error):
    return error_response(
        message=error.message,
        code=error.code,
        http_status=error.http_status,
        data=error.data,
    )


def handle_business_errors(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except BusinessError as error:
            return business_error_response(error)

    return wrapper
