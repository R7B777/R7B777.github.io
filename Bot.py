import os
import discord
from discord.ext import commands
import logging
from utils.logger import setup_logger
from utils.database import db
from models import Base

# Setup logging
logger = setup_logger()

# Initialize bot with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Load cogs
initial_extensions = [
    'cogs.moderation',
    'cogs.channels',
    'cogs.roles',
    'cogs.games',
    'cogs.warnings',
    'cogs.applications',
    'cogs.utility',
    'cogs.tickets'  # Add the new tickets cog
]

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    # Set status to Do Not Disturb and activity to "Listening to 1nfern0 <3"
    activity = discord.Activity(type=discord.ActivityType.listening, name="1nfern0 <3")
    await bot.change_presence(status=discord.Status.dnd, activity=activity)

    # Create database tables
    try:
        logger.info("Verifying database connection and tables...")
        Base.metadata.create_all(db.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.error("Database initialization failed, but bot will continue running")

    # Load all cogs
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f'Loaded extension {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}: {str(e)}')

    # Sync slash commands
    try:
        logger.info("Syncing slash commands...")
        await bot.tree.sync()
        logger.info("Slash commands synced successfully")
    except Exception as e:
        logger.error(f"Error syncing slash commands: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    else:
        logger.error(f'Unhandled error: {str(error)}')
        await ctx.send("An error occurred while executing the command.")

@bot.command(name='ping')
async def ping(ctx):
    """Check bot's latency"""
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("No Discord token found in environment variables!")
        exit(1)

    try:
        logger.info("Starting bot...")
        bot.run(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
