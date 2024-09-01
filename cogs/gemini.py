import discord
from discord.ext import commands
from discord import app_commands
from utils import gemini_api, helpers

class Gemini(commands.Cog, name="gemini"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Add slash and prefix command to the chat function
    @commands.hybrid_command(name="gemini", with_app_command=True, description="Chat with Gemini - for accessing images in history")
    @app_commands.describe(message="The message to send to Gemini (if you have attachments, just use @mention for your query)")
    async def chat_command(self, ctx: commands.Context, *, message: str):
        cleaned_text = message
        response_text = await gemini_api.generate_multimodal_response(cleaned_text, None, ctx.author.id)
        await self.send_response(ctx, response_text)

    async def send_response(self, ctx: commands.Context, response: str):
        # Slash command: discord.ext.commands.Context with ctx.interaction
        if ctx.interaction:
            await helpers.split_and_send_messages(ctx.interaction, response)
        # Prefix or mention without ctx.interaction
        else:
            await helpers.split_and_send_messages(ctx, response)


async def setup(bot) -> None:
    await bot.add_cog(Gemini(bot))
