import discord
from discord.ext import commands
from discord import app_commands
from utils import memory, groq_api, helpers
import os

MAX_HISTORY = int(os.getenv("MAX_HISTORY", 0))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))


class Llama(commands.Cog, name="llama"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.message_history = memory.load_memory()


    # Add slash and prefix command to the chat function
    @commands.hybrid_command(name="chat", with_app_command=True, description="Chat with Llama - limited to text")
    @app_commands.describe(message="The message to send to Llama", attachment="Attach or Paste in an optional text file")
    async def chat_command(self, ctx: commands.Context, *, message: str, attachment: discord.Attachment = None):
        cleaned_text = message
        try:
            if attachment:
                cleaned_text += await self.handle_attachment(attachment)
            response_text = await self.generate_response(ctx.author.id, cleaned_text)
            await self.send_response(ctx, response_text)
        except ValueError as e:
            await self.send_response(ctx, str(e))

    async def send_response(self, ctx: commands.Context, response: str):
        # Slash command: discord.ext.commands.Context with ctx.interaction
        if ctx.interaction:
            await helpers.split_and_send_messages(ctx.interaction, response)
        # Prefix or mention without ctx.interaction
        else:
            await helpers.split_and_send_messages(ctx, response)


    @commands.hybrid_command(name="reset", with_app_command=True, description="Reset your chat history")
    async def reset_command(self, ctx: commands.Context):
        await self.reset_user_history(ctx.author.id)
        await ctx.send(f"Message History Reset for user: {ctx.author.name}")

    
    # Called by both slash command and @mention
    async def generate_response(self, user_id, cleaned_text):
        user_id = str(user_id)

        # If history is disabled, just send a response
        if MAX_HISTORY == 0:
            return await groq_api.generate_response_groq(cleaned_text)

        # Add user's question to history
        memory.update_message_history(self.message_history, user_id, "user", cleaned_text)
        response_text = await groq_api.generate_response_groq(memory.get_formatted_message_history(self.message_history, user_id))
        
        # Add AI response to history
        memory.update_message_history(self.message_history, user_id, "assistant (L)", response_text)
        memory.save_memory(self.message_history)
        return response_text

    async def reset_user_history(self, user_id):
        user_id = str(user_id)
        if user_id in self.message_history:
            del self.message_history[user_id]
        memory.save_memory(self.message_history)

    async def handle_attachment(self, attachment: discord.Attachment) -> str:
        if attachment.filename.endswith('.txt'):
            file_contents = await attachment.read()
            return '\n' + file_contents.decode('utf-8')
        elif any(attachment.filename.lower().endswith(ext) for ext in sum(helpers.gemini_attachments, [])):
            raise ValueError(f"File type unsupported by Llama: your prompt will instead be sent to Gemini.\n *note: this may take longer than an average Llama 3 response*")
        else:
            raise ValueError(f"Unsupported file type. Please upload a .txt file.")


async def setup(bot) -> None:
    await bot.add_cog(Llama(bot))
