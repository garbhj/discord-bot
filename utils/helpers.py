import re
import discord
from discord.ext import commands

llama_attatchments = ["txt"]
gemini_attachments = [['.png', '.jpg', '.jpeg', '.gif', '.webp'], ['.mp3', '.wav', '.ogg']]

# Clean a Discord message by removing the userID between these brackets <>
def clean_discord_message(input_string):
    bracket_pattern = re.compile(r'<[^>]+>')
    return bracket_pattern.sub('', input_string)

# Handle different types of attachments
async def handle_attachment(attachment):
    if attachment.filename.endswith('.txt'):
        file_contents = await attachment.read()
        return '\n' + file_contents.decode('utf-8')
    # TODO: Add more attachment types
    else: 
        raise ValueError('Unsupported file time: please upload a .txt file')

# # Split and send messages to avoid exceeding Discord's message length limit
# async def split_and_send_messages(message, text, max_length=2000):
#     messages = [text[i:i + max_length] for i in range(0, len(text), max_length)]
#     for msg in messages:
#         # await message_system.channel.send(msg)
#         await message.reply(msg)

async def split_and_send_messages(ctx, text, max_length=2000):
    messages = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    for msg in messages:
        # discord.Interaction refers to slash commands
        if isinstance(ctx, discord.Interaction):
            print("SLASH COMMAND")
            if ctx.response.is_done():
                await ctx.followup.send(msg)
            else:
                await ctx.response.send_message(msg)
        # If called by prefix command
        elif isinstance(ctx, commands.Context):
            await ctx.reply(msg)
        # If called by @mention in a message
        elif isinstance(ctx, discord.Message):
            await ctx.reply(msg)
        else:
            raise ValueError("Unsupported context type")


# Process audio data (placeholder function)
async def process_audio(audio_data, text):
    # Implement your audio processing logic here
    return "Processed audio data with text: " + text
