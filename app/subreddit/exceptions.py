from app.exceptions import BaseError


class SubredditNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="Subreddit Not Found!")


class SubredditNameAlreadyExist(BaseError):
    def __init__(self):
        super().__init__(status_code=400, message="Subreddit Name Arelady Exist!")
