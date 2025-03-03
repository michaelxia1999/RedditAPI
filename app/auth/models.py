from app.models import Model


class TokenOut(Model):
    token: str
    exp: int


class TokenIn(Model):
    token: str


class SignInCredentials(Model):
    username: str
    password: str


class SignInResponse(Model):
    access_token: TokenOut
    refresh_token: TokenOut
