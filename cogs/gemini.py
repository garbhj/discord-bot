import discord
from discord.ext import commands
import aiohttp
from utils import gemini_api, helpers

class Gemini(commands.Cog, name="gemini"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return
        
        # Check for attachments
        if message.attachments and (self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
            async with message.channel.typing():
                cleaned_text = helpers.clean_discord_message(message.content)
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')
                        await self.handle_image_attachment(message, attachment, cleaned_text)
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                        await message.add_reaction('🎵')
                        await self.handle_audio_attachment(message, attachment, cleaned_text)

    async def handle_image_attachment(self, message, attachment, cleaned_text):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the image.')
                    return
                image_data = await resp.read()
                response_text = await gemini_api.generate_response_with_image_and_text(image_data, cleaned_text)
                await helpers.split_and_send_messages(message, response_text)

    async def handle_audio_attachment(self, message, attachment, cleaned_text):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the audio.')
                    return
                audio_data = await resp.read()
                response_text = await helpers.process_audio(audio_data, cleaned_text)
                await helpers.split_and_send_messages(message, response_text)

async def setup(bot) -> None:
    await bot.add_cog(Gemini(bot))
