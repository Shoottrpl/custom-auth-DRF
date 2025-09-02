class AuthenticationError(Exception):
    pass

class InvalidCredentialsError(AuthenticationError):
    pass

class InactiveUserError(AuthenticationError):
    pass

class TokenBlackListError(AuthenticationError):
    pass