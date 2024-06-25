__all__ = (
    'McRconDcException',
    'MissingEnvVarException',
    'NoDbConnectionException',
)


class McRconDcException(Exception):
    pass


class MissingEnvVarException(McRconDcException):
    pass


class DataBaseException(McRconDcException):
    pass


class NoDbConnectionException(DataBaseException):
    pass

