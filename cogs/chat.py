import discord
from discord.ext import commands
from utils import memory, helpers

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
            
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.filename.endswith('.txt'):
                        cleaned_text += await self.handle_text_attachment(attachment)
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')
                        await self.handle_image(message, attachment, cleaned_text)
                        return
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                        await message.add_reaction('🎵')
                        await self.handle_audio(message, attachment, cleaned_text)
                        return

            # No image or audio attachments, use Llama
            response_text = await self.generate_llama_response(message.author.id, cleaned_text)
            await helpers.split_and_send_messages(message, response_text)

    async def handle_text_attachment(self, attachment: discord.Attachment) -> str:
        if attachment.filename.endswith('.txt'):
            file_contents = await attachment.read()
            return '\n' + file_contents.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type. Please upload a .txt file.")

    async def handle_image(self, message, attachment, cleaned_text):
        gemini_cog = self.bot.get_cog('gemini')
        await gemini_cog.handle_image_attachment(message, attachment, cleaned_text)

    # TODO: audio does not yet work
    async def handle_audio(self, message, attachment, cleaned_text):
        gemini_cog = self.bot.get_cog('gemini')
        await gemini_cog.handle_audio_attachment(message, attachment, cleaned_text)

    async def generate_llama_response(self, user_id, cleaned_text):
        llama_cog = self.bot.get_cog('llama')
        return await llama_cog.generate_response(user_id, cleaned_text)

async def setup(bot):
    await bot.add_cog(Chat(bot))