from sqlite3 import connect, Cursor, Connection

from ..Exceptions import NoDbConnectionException


__all__ = (
    'DataBase',
)


class DataBase:
    """DataBase connection class"""
    __singleton: 'DataBase' = None

    def __new__(cls, *args, **kwargs):
        if cls.__singleton is None:
            cls.__singleton = super().__new__(cls)

        return cls.__singleton

    def __init__(self, file: str):
        """
        Args:
            file (str):
                data base file path
        """
        self.__conn = connect(file)
        self.__c = self.__conn.cursor()

        with open('mcrcondc/db/load.sql', 'r') as load:
            self.__c.executescript(load.read())
            self.__conn.commit()

    @property
    def conn(self) -> Connection:
        return self.__conn

    @property
    def c(self) -> Cursor:
        return self.c

    @classmethod
    def get_instance(cls) -> 'DataBase':
        """get the cursor of the database"""
        if (instance := cls.__singleton) is None:
            raise NoDbConnectionException("There is no data base connection, initialise the class once before "
                                          "executing queries.")

        return instance

    def __del__(self):
        self.__c.close()
        self.__conn.commit()
