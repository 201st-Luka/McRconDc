from urllib.parse import quote

from aiohttp import ClientSession

from mcrcondc.McRconDcExceptions import MojangApiError


__all__ = (
    'UsernameToUuid',
)


class UsernameToUuid:
    def __init__(self, name: str):
        self.__name = name
        self.__uuid = None

    async def request(self, session: ClientSession) -> dict:
        async with session.get("/users/profiles/minecraft/" + quote(self.__uuid)) as request:
            json = await request.json()

            if request.status == 200:
                self.__uuid = json['id']

                return json

            else:
                raise MojangApiError(json)

    @property
    def name(self):
        return self.__name

    @property
    def uuid(self):
        return self.__uuid
