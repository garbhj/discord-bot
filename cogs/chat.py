import discord
from discord.ext import commands
from utils import memory, helpers, gemini_api


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
            attachements = []

            if message.attachments:
                for attachment in message.attachments:
                    # TODO: Implement potential web retrieval and pdf reading
                    if attachment.filename.endswith('.txt'):
                        cleaned_text += await self.handle_text_attachment(attachment)
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                        await message.add_reaction('🎨')
                        attachements.append(await self.handle_image(message, attachment))
                    elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                        await message.add_reaction('🎵')
                        attachements.append(await self.handle_audio(message, attachment))

            if attachements != []:
                print(len(attachements))
                gemini_api.generate_multimodal_response(cleaned_text, attachements)

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

    async def handle_image(self, message, attachment):
        gemini_cog = self.bot.get_cog('gemini')
        return await gemini_cog.get_image_attachment(message, attachment)

    # TODO: audio does not yet work
    async def handle_audio(self, message, attachment):
        gemini_cog = self.bot.get_cog('gemini')
        return await gemini_cog.get_audio_attachment(message, attachment)

    async def generate_llama_response(self, user_id, cleaned_text):
        llama_cog = self.bot.get_cog('llama')
        return await llama_cog.generate_response(user_id, cleaned_text)

async def setup(bot):
    await bot.add_cog(Chat(bot))