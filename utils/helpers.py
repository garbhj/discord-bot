import re
import discord

# Clean a Discord message by removing text between brackets
def clean_discord_message(input_string):
    bracket_pattern = re.compile(r'<[^>]+>')
    return bracket_pattern.sub('', input_string)

# Handle different types of attachments
async def handle_attachment(attachment):
    if attachment.filename.endswith('.txt'):
        file_contents = await attachment.read()
        return '\n' + file_contents.decode('utf-8')
    # Add more attachment types as needed
    return ''

# Split and send messages to avoid exceeding Discord's message length limit
async def split_and_send_messages(message_system, text, max_length=2000):
    messages = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    for msg in messages:
        await message_system.channel.send(msg)

# Process audio data (placeholder function)
async def process_audio(audio_data, text):
    # Implement your audio processing logic here
    return "Processed audio data with text: " + text
