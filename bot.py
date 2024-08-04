"""
Credits (modified from): 

Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python
"""


import os
import json
import logging
import platform
import random

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
prefix = config.get("prefix", "!")
invite_link = config.get("invite_link", "")

# Set up intents (including for slash commands)
intents = discord.Intents.default()
intents.message_content = True

# Custom logging formatter for colored log output
class LoggingFormatter(logging.Formatter):
    # Colors and styles for log levels
    COLORS = {
        logging.DEBUG: "\x1b[38m\x1b[1m",  # Gray bold
        logging.INFO: "\x1b[34m\x1b[1m",   # Blue bold
        logging.WARNING: "\x1b[33m\x1b[1m",  # Yellow bold
        logging.ERROR: "\x1b[31m",         # Red
        logging.CRITICAL: "\x1b[31m\x1b[1m"  # Red bold
    }
    RESET = "\x1b[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.RESET)
        formatter = logging.Formatter(
            f"{log_color}{{asctime}}{self.RESET} {{levelname:<8}} {{name}}: {{message}}", 
            "%Y-%m-%d %H:%M:%S", 
            style="{"
        )
        return formatter.format(record)

# Set up logging
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler.setFormatter(logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
))
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Bot class
class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix, intents=intents, help_command=None)
        self.logger = logger
        self.config = config
        self.database = None  # Placeholder for database connection

    # Database initialization
    async def init_db(self):
        # TODO: Implement database
        pass

    # Load all cogs/extensions
    async def load_cogs(self):
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    self.logger.error(f"Failed to load extension {extension}: {e}")

    # Change bot status periodically
    @tasks.loop(minutes=1.0)
    async def status_task(self):
        statuses = ["with you!", "with Krypton!", "with humans!"]
        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self):
        await self.wait_until_ready()

    # Setup hook for initial setup
    async def setup_hook(self):
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        self.logger.info("-------------------")
        await self.init_db()
        await self.load_cogs()
        self.status_task.start()

        await self.tree.sync()
        self.logger.info(f"Synced commands for {self.user.name}")


    # Handle messages
    async def on_message(self, message: discord.Message):
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    # Log command completion
    async def on_command_completion(self, context: commands.Context):
        full_command_name = context.command.qualified_name
        executed_command = full_command_name.split(" ")[0]
        if context.guild:
            self.logger.info(f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
        else:
            self.logger.info(f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")

    # Handle command errors
    async def on_command_error(self, context: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if hours else ''} {f'{round(minutes)} minutes' if minutes else ''} {f'{round(seconds)} seconds' if seconds else ''}.", color=0xE02B2B)
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(description="You are not the owner of the bot!", color=0xE02B2B)
            await context.send(embed=embed)
            self.logger.warning(f"{context.author} tried to execute an owner-only command.")
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"You are missing the permission(s) `{', '.join(error.missing_permissions)}` to execute this command!", color=0xE02B2B)
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description=f"I am missing the permission(s) `{', '.join(error.missing_permissions)}` to fully perform this command!", color=0xE02B2B)
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Error!", description=str(error).capitalize(), color=0xE02B2B)
            await context.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            command_name = str(error).split('"')[1]  # Extract command name from error message
            embed = discord.Embed(title="Command Not Found", description=f"The command `{command_name}` was not found. Please check the command name and try again.", color=0xE02B2B)
            await context.send(embed=embed)
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            embed = discord.Embed(title="Error!", description=str(error.original), color=0xE02B2B)
            await context.send(embed=embed)
        else:
            self.logger.error(f"An unexpected error occurred: {error}")
            await context.reply("An unexpected error occurred. Please try again later.", ephemeral=True)

# Initialize and run the bot
bot = DiscordBot()
bot.run(DISCORD_BOT_TOKEN)
