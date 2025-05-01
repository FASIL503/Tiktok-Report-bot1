import discord
from discord.ext import commands
import asyncio
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# Nuke configuration
delete_concurrency = 5  # Number of concurrent delete operations

async def bulk_delete_channels(guild: discord.Guild):
    sem = asyncio.Semaphore(delete_concurrency)
    tasks = []
    for channel in guild.channels:
        async def _del(ch):
            async with sem:
                try:
                    await ch.delete()
                except Exception as e:
                    logging.error(f"Channel delete failed: {e}")
        tasks.append(asyncio.create_task(_del(channel)))
    await asyncio.gather(*tasks)

async def bulk_delete_roles(guild: discord.Guild):
    sem = asyncio.Semaphore(delete_concurrency)
    tasks = []
    for role in guild.roles:
        async def _del(r):
            async with sem:
                try:
                    await r.delete()
                except Exception as e:
                    logging.error(f"Role delete failed: {e}")
        tasks.append(asyncio.create_task(_del(role)))
    await asyncio.gather(*tasks)

async def bulk_ban_members(guild: discord.Guild):
    sem = asyncio.Semaphore(delete_concurrency)
    tasks = []
    for member in guild.members:
        if member.bot or member == guild.me:
            continue
        async def _ban(m):
            async with sem:
                try:
                    await guild.ban(m)
                except Exception as e:
                    logging.error(f"Ban failed: {e}")
        tasks.append(asyncio.create_task(_ban(member)))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if not isinstance(r, Exception))

async def create_roles(guild: discord.Guild, name: str, count: int = 50):
    sem = asyncio.Semaphore(delete_concurrency)
    tasks = []
    for _ in range(count):
        async def _create():
            async with sem:
                try:
                    await guild.create_role(name=name)
                except Exception as e:
                    logging.error(f"Role create failed: {e}")
        tasks.append(asyncio.create_task(_create()))
    await asyncio.gather(*tasks)

async def create_voice_channels(guild: discord.Guild, name: str, count: int = 20):
    sem = asyncio.Semaphore(delete_concurrency)
    tasks = []
    for _ in range(count):
        async def _create():
            async with sem:
                try:
                    await guild.create_voice_channel(name=name)
                except Exception as e:
                    logging.error(f"Voice channel create failed: {e}")
        tasks.append(asyncio.create_task(_create()))
    await asyncio.gather(*tasks)

async def nuke_guild(guild: discord.Guild, name: str):
    logging.info(f"Nuking guild: {guild.name} ({guild.id})")
    banned_count = await bulk_ban_members(guild)
    logging.info(f"Members banned: {banned_count}")
    await bulk_delete_channels(guild)
    logging.info("Channels deleted")
    await bulk_delete_roles(guild)
    logging.info("Roles deleted")
    await create_voice_channels(guild, name)
    logging.info("Voice channels created")
    await create_roles(guild, name)
    logging.info("Roles created")

@bot.command(name='nuke', help='Nuke the entire server')
@commands.has_permissions(administrator=True)
async def nuke(ctx: commands.Context):
    await ctx.message.delete()
    confirm = await ctx.send('Are you sure you want to nuke this server? Reply with `yes` within 15 seconds.')

    def check(m):
        return m.author == ctx.author and m.content.lower() == 'yes' and m.channel == ctx.channel

    try:
        await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        return await ctx.send('Nuke canceled.')

    await nuke_guild(ctx.guild, name=ctx.guild.name)
    await ctx.send('Server nuked.')

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} | Connected to {len(bot.guilds)} guilds")

if __name__ == '__main__':
    token = input('Enter bot token: ')
    bot.run(token)
