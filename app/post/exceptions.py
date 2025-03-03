from app.exceptions import BaseError


class PostNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Post Not Found!")


class PostUpvoteNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Post Vote Not Found!")
