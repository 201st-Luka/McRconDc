from asyncio import gather
from sqlite3 import IntegrityError
from urllib.parse import quote

from interactions import (Extension, slash_command, SlashContext, OptionType, slash_option, SlashCommand,
                          SlashCommandOption, Embed, AutocompleteContext, EmbedField, SlashCommandChoice)
from interactions.ext.paginators import Paginator
from aiohttp import ClientSession

from mojang_api import UuidToUsername
from ..db import DataBase


class Link(Extension):
    """
    Command extension for linking the Minecraft accounts and servers
    """

    def __init__(self, bot, api: ClientSession):
        self.session = api

    link = SlashCommand(name="link")

    user = link.group(name="user")

    @user.subcommand(sub_cmd_name="add",
                     sub_cmd_description="Links a minecraft account to a discord user",
                     options=[
                         SlashCommandOption(
                             name="mc_account_name",
                             type=OptionType.STRING,
                             description="Minecraft username",
                             required=True,
                         ),
                     ])
    async def add(self, ctx: SlashContext, mc_account_name: str):
        """
        Links the user's discord to a minecraft account

        Args:
            ctx:
                The slash command context
            mc_account_name:
                Minecraft username
        """
        async with self.session.get(quote("/users/profiles/minecraft/" + mc_account_name)) as response:

            if response.status == 200:
                json = await response.json()
                uuid = json['id']

                db = DataBase.get_instance()

                try:
                    db.conn.execute("INSERT INTO DiscordServer (server_id) VALUES(:id);",
                                    {'id': ctx.guild_id})
                except IntegrityError:
                    pass

                # The MC account could already be in the database
                try:

                    db.conn.execute("INSERT INTO MinecraftAccount (uuid) VALUES(:uuid);",
                                    {'uuid': uuid})
                except IntegrityError:
                    pass

                # The DD account could already be in the database
                try:
                    db.conn.execute("INSERT INTO DiscordAccount (user_id) VALUES (:id);",
                                    {'id': ctx.user.id})
                except IntegrityError:
                    pass

                try:
                    db.conn.execute("INSERT INTO Member (user_id, server_id) VALUES (:user, :server);",
                                    {'user': ctx.user.id, 'server': ctx.guild_id})
                except IntegrityError:
                    pass

                # Linking
                try:
                    db.conn.execute("INSERT INTO Link (uuid, user_id) VALUES(:uuid, :id);",
                                    {'uuid': uuid, 'id': ctx.user.id})

                    db.conn.commit()
                    await ctx.send("Link successful.")

                except IntegrityError:
                    await ctx.send("Account already linked.")

            else:
                await ctx.send("Invalid username.")

    @user.subcommand(sub_cmd_name="remove",
                     sub_cmd_description="Removes a minecraft account from a discord user",
                     options=[
                         SlashCommandOption(
                             name="mc_account_name",
                             type=OptionType.STRING,
                             description="Minecraft username",
                             required=True,
                             autocomplete=True
                         ),
                     ])
    async def remove(self, ctx: SlashContext, mc_account_name: str):
        """
        Removes the link between the user's discord account and (one of) his minecraft account(s)

        Args:
            ctx:
                The slash command context
            mc_account_name:
                Minecraft username
        """
        async with self.session.get(quote("/users/profiles/minecraft/" + mc_account_name)) as response:

            if response.status == 200:
                json = await response.json()
                uuid = json['id']

                db = DataBase.get_instance()
                try:

                    db.conn.execute("DELETE FROM Link WHERE uuid = :uuid AND user_id = :id;",
                                    {'uuid': uuid, 'id': ctx.user.id})

                    db.conn.commit()

                    await ctx.send("Delete successful.")

                except IntegrityError:
                    await ctx.send("Account not linked to you.")

            else:
                await ctx.send("Invalid username.")

    @remove.autocomplete("mc_account_name")
    async def autocomplete(self, ctx: AutocompleteContext):
        """
        Autocompletes a user's minecraft accounts

        Args:
            ctx:
                The auto complete context
        """

        db = DataBase.get_instance()

        query = db.conn.execute("SELECT uuid FROM Link WHERE user_id = :id;",
                                {'id': ctx.user.id})

        result = query.fetchall()

        requests = [UuidToUsername(r[0]).request(self.session) for r in result]
        responses = await gather(*requests)
        usernames = [r['name'] for r in responses]

        await ctx.send(choices=usernames[:25])

    @user.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="Lists every minecraft account for the Discord user",
    )
    async def list(self, ctx: SlashContext) -> None:
        """
        List all linked Minecraft accounts of one Discord user

        Args:
            ctx:
                The slash command context
        """
        db = DataBase.get_instance()

        # Get all uuids of the Minecraft accounts
        query = db.conn.execute("SELECT uuid FROM Link WHERE user_id = :user_id;",
                                {'user_id': ctx.user.id})
        uuids = query.fetchall()

        # Respond to the Discord User no account is linked
        if not len(uuids):
            await ctx.send("You don't have any linked accounts. You can do so by using `/link user add "
                           "<mc_account_name>`.")
            return

        # Fetch Minecraft account names
        accounts = [UuidToUsername(uuid[0]).request(self.session) for uuid in uuids]
        responses = await gather(*accounts)

        # Slice the data into smaller pieces
        response_slices = [responses[i:i + 5] for i in range(0, len(responses), 5)]
        embed_fields = [
            [EmbedField(name=r['name'], value=r['name']) for r in response_slice]
            for response_slice in response_slices
        ]
        # Create embeds for the data
        embeds = [
            Embed(
                title=f"Accounts of {ctx.user.display_name}",
                description=f"The user **{ctx.user.display_name}** has {len(response_slice)} account"
                            f"{'s' if len(response_slice) != 1 else ''}.",
                fields=fields
            ) for fields, response_slice in zip(embed_fields, response_slices)
        ]

        # Send data to the user in for of a single embed or pagination
        if len(embeds) > 1:
            paginator = Paginator.create_from_embeds(self.bot, *embeds)

            await paginator.send(ctx)
        else:
            await ctx.send(embeds=embeds)

    server = link.group(name="server")

    @server.subcommand(
        sub_cmd_name="add",
        sub_cmd_description="Adds a minecraft server to the current discord server",
        options=[
            SlashCommandOption(
                name="ip",
                type=OptionType.STRING,
                description="The server's IP address or URL",
                required=True,
            ),
            SlashCommandOption(
                name="name",
                type=OptionType.STRING,
                description="The server's name",
                required=True,
            ),
            SlashCommandOption(
                name="password",
                type=OptionType.STRING,
                description="The server's password",
                required=True,
            ),
        ])
    async def add_server(self, ctx: SlashContext, ip: str, name: str, password: str):
        db = DataBase.get_instance()

        try:
            db.conn.execute("INSERT INTO DiscordServer (server_id) VALUES(:id);",
                            {'id': ctx.guild_id})
        except IntegrityError:
            pass

        try:
            db.conn.execute("INSERT INTO MinecraftServer (ip, name, password) VALUES(:ip, :name, :password);",
                            {'ip': ip, 'name': name, 'password': password})
        except IntegrityError:
            pass

        try:
            db.conn.execute("INSERT INTO Manages (ip, server_id) VALUES(:ip, :id)",
                            {'id': ctx.guild_id, 'ip': ip})
            await ctx.send("Minecraft server successfully linked to this discord server.")
            db.conn.commit()
        except IntegrityError:
            await ctx.send("Minecraft server already linked to this discord server.")

    @server.subcommand(sub_cmd_name="remove",
                       sub_cmd_description="Unlinks a Minecraft server from this discord server",
                       options=[
                           SlashCommandOption(
                               name="ip",
                               type=OptionType.STRING,
                               description="The server's IP address or URL",
                               required=True,
                               autocomplete=True
                           )]
                       )
    async def remove_server(self, ctx: SlashContext, ip: str):
        db = DataBase.get_instance()

        try:
            db.conn.execute("DELETE FROM Manages WHERE ip = :ip AND server_id = :id;",
                            {'ip': ip, 'id': ctx.guild_id})
            await ctx.send("Server successfully deleted")
            db.conn.commit()

        except IntegrityError:
            await ctx.send("Server not found")

    @remove_server.autocomplete("ip")
    async def autocomplete(self, ctx: AutocompleteContext):

        db = DataBase.get_instance()

        query = db.conn.execute("SELECT ip FROM Manages WHERE server_id = :id;",
                                {'id': ctx.guild_id})

        result = query.fetchall()

        await ctx.send(choices=result[0][:25])


def setup(bot, api=None):
    Link(bot, api)
