from app.exceptions import BaseError


class UsernameAlreadyExist(BaseError):
    def __init__(self):
        super().__init__(status_code=400, message="Usrname Already Exist!")


class DisplayNameAlreadyExist(BaseError):
    def __init__(self):
        super().__init__(status_code=400, message="Display Name Already Exist!")


class EmailAlreadyExist(BaseError):
    def __init__(self):
        super().__init__(status_code=400, message="Email Already Exist!")


class UserNotFound(BaseError):
    def __init__(self):
        super().__init__(status_code=404, message="User Not Found!")
