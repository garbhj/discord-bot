import discord
from discord.ext import commands
import aiohttp
from utils import gemini_api, helpers

class Gemini(commands.Cog, name="gemini"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def handle_attachments(self, message: discord.Message):
        async with message.channel.typing():
            cleaned_text = helpers.clean_discord_message(message.content)
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    await message.add_reaction('🎨')
                    await self.handle_image_attachment(message, attachment, cleaned_text)
                elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                    await message.add_reaction('🎵')
                    await self.handle_audio_attachment(message, attachment, cleaned_text)

    # TODO: Redo all of these functions
    async def handle_image_attachment(self, message, attachment, cleaned_text):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the image.')
                    return
                image_data = await resp.read()
                response_text = await gemini_api.generate_response_with_image_and_text(image_data, cleaned_text)
                await helpers.split_and_send_messages(message, response_text)
    
    # TODO: Add audio handling
    async def handle_audio_attachment(self, message, attachment, cleaned_text):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the audio.')
                    return
                audio_data = await resp.read()
                response_text = await helpers.process_audio(audio_data, cleaned_text)
                await helpers.split_and_send_messages(message, response_text)

    # I'm just making these new funcctions for multiple attachements as I don't want to mess up the existing funtionality         

    async def get_image_attachment(self, message, attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the image.')
                    return
                image_data = await resp.read()
                return image_data
    
    # TODO: Add audio handling
    async def get_audio_attachment(self, message, attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the audio.')
                    return
                audio_data = await resp.read()
                return audio_data

async def setup(bot) -> None:
    await bot.add_cog(Gemini(bot))
