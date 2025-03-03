from app.exceptions import BaseError


class AuthenticationFailed(BaseError):
    def __init__(self):
        super().__init__(status_code=401, message="Authentication Failed!")
