from rest_framework import status


class BusinessError(Exception):
    def __init__(
        self,
        message,
        code=40000,
        http_status=status.HTTP_400_BAD_REQUEST,
        data=None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status
        self.data = data
