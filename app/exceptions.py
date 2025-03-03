class BaseError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def content(self):
        return {"message": self.message}


class RateLimitExceeded(BaseError):
    def __init__(self):
        super().__init__(status_code=429, message="Rate limit exceeded. Try again later.")
