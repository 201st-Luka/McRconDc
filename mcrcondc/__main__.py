from os import environ, path

from .Exceptions import McRconDcException, MissingEnvVarException
from . import McRconDc


# get env varibales
token = environ.get("TOKEN")
if token is None:
    raise MissingEnvVarException("The environment variable 'TOKEN' must be specified and must be set to the "
                                 "Discord authentication token.")

log_path = environ.get("LOG_PATH")
if log_path is None:
    raise MissingEnvVarException("The environment variable 'LOG_PATH' must be specified and must be set to "
                                 "the log folder path.")
if not path.isdir(log_path):
    raise McRconDcException("The log folder path is invalid.")

db_file = environ.get("DB_FILE")
if db_file is None:
    raise McRconDcException("The environment variable 'DB_FILE' must be specified and must be set to the data base "
                            "file path.")

# create client
client = McRconDc(token, log_path, db_file, "mcrcondc.extensions", debug=environ.get("DEBUG"))

# start client
client.start()
