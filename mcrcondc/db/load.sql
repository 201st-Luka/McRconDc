--Represents a Discord server
CREATE TABLE IF NOT EXISTS DiscordServer(
    server_id INTEGER PRIMARY KEY
);

--Represents a Minecraft server
CREATE TABLE IF NOT EXISTS MinecraftServer(
    ip TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    password BLOB NOT NULL
);

--Represents a Discord account
CREATE TABLE IF NOT EXISTS DiscordAccount(
    user_id TEXT PRIMARY KEY
);

--Represents a Minecraft account
CREATE TABLE IF NOT EXISTS MinecraftAccount(
    uuid TEXT PRIMARY KEY
);

--Represents a member of a discord server
CREATE TABLE IF NOT EXISTS Member(
    user_id TEXT NOT NULL,
    server_id TEXT NOT NULL,
    PRIMARY KEY (user_id, server_id),
    FOREIGN KEY (server_id) REFERENCES DiscordServer(server_id),
    FOREIGN KEY (user_id) REFERENCES DiscordAccount(user_id)
);

--Represents what MC account is linked to what DD account
CREATE TABLE IF NOT EXISTS Link(
    uuid TEXT NOT NULL,
    user_id TEXT NOT NULL,
    PRIMARY KEY (user_id, uuid),
    FOREIGN KEY (uuid) REFERENCES MinecraftAccount(uuid),
    FOREIGN KEY (user_id) REFERENCES DiscordAccount(user_id)
);

--Represents the minecraft accounts whitelisted on a server
CREATE TABLE IF NOT EXISTS Whitelist(
    ip TEXT NOT NULL,
    uuid TEXT NOT NULL,
    PRIMARY KEY (ip, uuid),
    FOREIGN KEY (ip) REFERENCES MinecraftServer(ip),
    FOREIGN KEY (uuid) REFERENCES MinecraftAccount(uuid)
);

--Represents all the minecraft servers that the bot manages on a discord server
CREATE TABLE IF NOT EXISTS Manages(
    ip TEXT NOT NULL,
    server_id TEXT NOT NULL,
    PRIMARY KEY (ip, server_id),
    FOREIGN KEY (ip) REFERENCES MinecraftServer(ip),
    FOREIGN KEY (server_id) REFERENCES DiscordServer(server_id)
);

--Represents the discord users who have permission to modify the whitelist
CREATE TABLE IF NOT EXISTS Permissions(
    ip TEXT NOT NULL,
    user_id TEXT NOT NULL,
    PRIMARY KEY (ip, user_id),
    FOREIGN KEY (user_id) REFERENCES DiscordAccount(user_id),
    FOREIGN KEY (ip) REFERENCES MinecraftServer(ip)
);

