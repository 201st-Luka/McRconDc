__all__ = (
    'McRconDcException',
    'MissingEnvVarException',
    'NoDbConnectionException',
    'MojangApiError',
)


class McRconDcException(Exception):
    pass


class MissingEnvVarException(McRconDcException):
    pass


class DataBaseException(McRconDcException):
    pass


class NoDbConnectionException(DataBaseException):
    pass


class MojangApiError(McRconDcException):
    pass

