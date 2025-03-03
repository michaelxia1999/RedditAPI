from app.exceptions import BaseError


class CommentNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Comment Not Found!")


class CommentUpvoteNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Comment Vote Not Found!")
