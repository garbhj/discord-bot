# Discord Bot using Groq API and Llama Model

This is a Discord Chatbot built using the discord.py library, as well as two LLM APIs to chat with users on discord. 

The first is Meta's Llama 3.1 70b, which is accessed from the super-fast Groq API but can only process text.
The second is Google Gemini, which is slower but multimodal.
To be honest, you can easily change the specific model used to any of the ones offered by the provider.

It keeps a chat history for each user, and can handle various tasks including processing messages, and analyzing text, image, and audio attachments. Attachments are stored in the message history and are accessible for 48 hours; however the files themselves can only be accessed by Gemini (Llama will only see the file names).

The system prompts that tell the AIs are stil a bit wonky; you may want to tweak these or remove them altogether.

### Commands
The bot can be called in a server using @mention, and responds to any message in DMs.

By default, any message recieved by the bot is automatically sent to either Llama or Gemini, depending on whether or not there are any attachements in the message recieved only. However, you can also specify the model you want to use with the following commands:
/gemini - For Google Gemini (For instance, when you want the model to reference past attachements)
/chat - For Llama (Super fast response time but text only)

The history keeps the text sent by both parties, as well as references to any attachements. To clear history, use the following command:
/reset

To test if the bot itself is working at all, use:
/test

## Setup

### Requirements

- Python 3.8 or higher
- Discord bot token
- Groq API key
- Gemini API key

### Installation

1. Clone the repository
2. Install required libraries 
3. Add the bot to your server
4. Setup .env with the required api keys
5. Run bot.py

## Credits
Some code, specificially error logging in bot.py, is from:
https://github.com/kkrypt0nn/Python-Discord-Bot-Template/tree/main

I was inspired to start this project when I saw this bot by Echoshard back in December:
https://github.com/Echoshard/Gemini_Discordbot