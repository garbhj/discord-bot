import discord
from discord.ext import commands
from utils import memory, helpers, gemini_api
import aiohttp


class Chat(commands.Cog, name="chat"):
    def __init__(self, bot):
        self.bot = bot
        self.message_history = memory.load_memory()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.mention_everyone:
            return

        if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            await self.process_message(message)

    async def process_message(self, message: discord.Message):
        async with message.channel.typing():
            cleaned_text = helpers.clean_discord_message(message.content)
            
            # TODO: Implement multiple attachments in the file
            # This will involve passing in a list of attachements, and conslidating image, audio, and video.
            attachments = []

            if message.attachments:
                for attachment in message.attachments:
                    # TODO: Implement potential web retrieval and pdf reading
                    if attachment.filename.endswith('.txt'):
                        cleaned_text += await self.handle_text_attachment(attachment)
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')
                        image_data = await self.get_image_attachment(message, attachment)
                        if image_data:
                            attachments.append({
                                'filename': attachment.filename,
                                'data': image_data,
                                'mime_type': attachment.content_type or 'image/jpeg'
                            })
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                        await message.add_reaction('🎵')
                        audio_data = await self.get_audio_attachment(message, attachment)
                        if audio_data:
                            attachments.append({
                                'filename': attachment.filename,
                                'data': audio_data,
                                'mime_type': attachment.content_type or 'audio/mpeg'
                            })

            if attachments != []:
                print(len(attachments))
                await gemini_api.generate_multimodal_response(cleaned_text, attachments)
            else:
                print("No attachments")
                # No image or audio attachments, use Llama
                response_text = await self.generate_llama_response(message.author.id, cleaned_text)
                await helpers.split_and_send_messages(message, response_text)

    async def handle_text_attachment(self, attachment: discord.Attachment) -> str:
        if attachment.filename.endswith('.txt'):
            file_contents = await attachment.read()
            return '\n' + file_contents.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type. Please upload a .txt file.")

    async def get_image_attachment(self, message, attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the image.')
                    return
                image_data = await resp.read()
                return image_data
    
    # TODO: Fix audio handling (doesn't work yet)
    async def get_audio_attachment(self, message, attachment):
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    await message.channel.send('Unable to download the audio.')
                    return
                audio_data = await resp.read()
                return audio_data

    async def generate_llama_response(self, user_id, cleaned_text):
        llama_cog = self.bot.get_cog('llama')
        return await llama_cog.generate_response(user_id, cleaned_text)

async def setup(bot):
    await bot.add_cog(Chat(bot))