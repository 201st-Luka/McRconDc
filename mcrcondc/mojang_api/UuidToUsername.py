from urllib.parse import quote

from aiohttp import ClientSession

from mcrcondc.McRconDcExceptions import MojangApiError


__all__ = (
    'UuidToUsername',
)


class UuidToUsername:
    def __init__(self, uuid: str):
        self.__uuid = uuid
        self.__name = None

    async def request(self, session: ClientSession) -> dict:
        async with session.get("/user/profile/" + quote(self.__uuid)) as request:
            json = await request.json()

            if request.status == 200:
                self.__name = json['name']

                return json

            else:
                raise MojangApiError(json)

    @property
    def name(self):
        return self.__name

    @property
    def uuid(self):
        return self.__uuid
