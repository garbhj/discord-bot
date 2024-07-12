import discord
from discord.ext import commands
from utils import memory, groq_api, helpers
import os

MAX_HISTORY = int(os.getenv("MAX_HISTORY"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

class Llama(commands.Cog, name="llama"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.message_history = memory.load_memory()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore messages from the bot itself or mentions of everyone
        if message.author == self.bot.user or message.mention_everyone:
            return
        
        # Check if the bot is mentioned or if the message is a DM
        if self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            cleaned_text = helpers.clean_discord_message(message.content)
            async with message.channel.typing():
                # Handle message attachments
                if message.attachments:
                    attachment = message.attachments[0]
                    cleaned_text += await helpers.handle_attachment(attachment)
                
                # Check for keyword reset
                if "RESET" in cleaned_text and len(cleaned_text) < 10:
                    self.reset_user_history(message.author.id)
                    await message.channel.send(f"Message History Reset for user: {message.author.name}")
                    return

                await message.add_reaction('💬')
                await self.handle_message(message, cleaned_text)

    async def handle_message(self, message, cleaned_text):
        user_id = message.author.id

        # If history is disabled, just send a response
        if MAX_HISTORY == 0:
            response_text = await groq_api.generate_response_groq(cleaned_text)
            await helpers.split_and_send_messages(message, response_text)
            return

        # Add user's question to history
        memory.update_message_history(self.message_history, user_id, "user", cleaned_text)
        response_text = await groq_api.generate_response_groq(memory.get_formatted_message_history(self.message_history, user_id))
        
        # Add AI response to history
        memory.update_message_history(self.message_history, user_id, "assistant", response_text)
        await helpers.split_and_send_messages(message, response_text)
        memory.save_memory(self.message_history)

    def reset_user_history(self, user_id):
        user_id = str(user_id)
        if user_id in self.message_history:
            del self.message_history[user_id]
        memory.save_memory(self.message_history)

async def setup(bot) -> None:
    await bot.add_cog(Llama(bot))
