from urllib.parse import quote

from interactions import (Extension, slash_command, SlashContext, OptionType, slash_option, SlashCommand,
                          SlashCommandOption)
from aiohttp import ClientSession

from ..db import DataBase


class Link(Extension):
    def __init__(self, bot, api: ClientSession):
        self.session = api

    link = SlashCommand(name="link")

    @link.subcommand(sub_cmd_name="user",
                     sub_cmd_description="Links a minecraft account to a discord user",
                     options=[
                         SlashCommandOption(
                             name="string_option",
                             type=OptionType.STRING,
                             description="String Option",
                             required=True
                         ),
                     ])
    async def user(self, ctx: SlashContext, string_option: str):
        async with self.session.get(quote("/users/profiles/minecraft/" + string_option)) as response:
            if response.status == 200:
                json = await response.json()
                uuid = json['id']

                db = DataBase.get_instance()
                db.conn.execute("INSERT INTO MinecraftAccount (uuid) VALUES(:uuid);",
                                {'uuid': uuid})
                db.conn.execute("INSERT INTO Link (uuid, user_id) VALUES(:uuid, :id);",
                                {'uuid': uuid, 'id': ctx.user.id})
                db.conn.commit()

                await ctx.send("Link successful.")

            else:
                await ctx.send("Invalid username.")


def setup(bot, api=None):
    Link(bot, api)
