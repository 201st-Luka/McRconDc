from asyncio import get_event_loop
from logging.handlers import TimedRotatingFileHandler
from os import path
from logging import Logger, INFO, DEBUG, Formatter, StreamHandler
from sys import stdout
from aiohttp import ClientSession, ClientTimeout

from coloredlogs import install
from interactions import Client, MISSING

from .db import DataBase


__all__ = (
    'McRconDc',
)


class CustomLogger(Logger):
    """
    Custom logger class that formats the log and creates the required streams
    """
    format_str = "[%(asctime)s]:  [%(levelname)s]:  [%(name)s]:\t%(message)s"
    field_styles = {
        'asctime': {'color': 'green'},
        'hostname': {'color': 'magenta'},
        'levelname': {'bold': True, 'color': 'white'},
        'name': {'color': 'blue'},
        'programname': {'color': 'cyan'},
        'username': {'color': 'yellow'}
    }
    suffix = "%Y_%m_%d"
    log_file = "McRconDc.log"

    def __init__(self, folder_path: str, debug: bool = False):
        """
        Args:
            folder_path (str):
                logging folder path
            debug (bool):
                enable debug mode
        """
        level = DEBUG if debug else INFO

        # initialise super class
        super().__init__(
            name="McRconDc",
            level=level
        )

        # format the log
        self.log_format = Formatter(self.format_str)

        # create the output handlers
        output_file_handler = TimedRotatingFileHandler(
            filename=path.join(folder_path, CustomLogger.log_file),
            when="midnight",
            backupCount=14,
        )
        output_file_handler.suffix = CustomLogger.suffix
        output_file_handler.setFormatter(
            self.log_format
        )

        console_handler = StreamHandler(stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self.log_format)

        self.addHandler(output_file_handler)
        self.addHandler(console_handler)

        # install colored logs
        install(
            level=level,
            logger=self,
            fmt=self.format_str,
            field_styles=self.field_styles
        )


class McRconDc(Client):
    """Custom Client class that implements the logger and load the extensions"""
    def __init__(self, token: str, log_path: str, db_file: str, extensions: str, debug: int = None,
                 request_timeout: ClientTimeout = ClientTimeout(connect=10)):
        """
        Args:
            token (str):
                Discord authentication token
            log_path (str):
                log folder path
            extensions (str):
                collection of extension packages
            debug (bool):
                enable debug mode
        """
        logger = CustomLogger(log_path, debug=debug is not None)

        super().__init__(
            token=token,
            logger=logger,
            sync_interactions=True,
            debug_scope=debug or MISSING
        )

        self.db = DataBase(db_file)
        self.__request_timeout = request_timeout
        self.__extensions = extensions
        self.mojang_api = None

    async def astart(self, token: str | None = None) -> None:
        loop = get_event_loop()

        self.mojang_api = ClientSession(
            base_url="https://api.mojang.com",
            loop=loop,
            timeout=self.__request_timeout
        )

        self.load_extension(f"{self.__extensions}.Link", api=self.mojang_api)

        await super().astart(token)

    async def stop(self):
        await self.mojang_api.close()
        self.db.c.close()
        self.db.conn.close()

        await super().stop()
