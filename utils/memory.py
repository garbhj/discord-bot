import json
import os


# Load configuration from environment variables
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 8000))

# Load memory from a JSON file
def load_memory():
    try:
        with open('GroqMemory.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"An error occurred when trying to load history: {e}")
        return {}

# Save memory to a JSON file
def save_memory(memory):
    with open('GroqMemory.json', 'w') as f:
        json.dump(memory, f, indent=4)

# Update message history
def update_message_history(message_history, user_id, role: str, text: str, attachments=None):
    user_id = str(user_id)
    if user_id not in message_history:
        message_history[user_id] = []

    new_message = {
        "role": role,
        "content": text
    }
    
    if attachments:
        new_message["attachments"] = [
            {
                "uri": attachment['uri'],
                "name": attachment['name'],
                "mime_type": attachment['mime_type']
            } for attachment in attachments
        ]

    # Estimate token count
    token_count = (len(text) + 3) // 4

    # Check if adding this message exceeds the limit
    while (token_count + 
           sum((len(msg.get("content", "")) + 3) // 4 + 
               len(msg.get("attachments", [])) * 258 
               for msg in message_history[user_id]) > MAX_TOKENS and 
           len(message_history[user_id]) > 2):
        del message_history[user_id][0]
        message_history[user_id].insert(0, {"role": "system", "content": "<message history truncated>"})

    message_history[user_id].append(new_message)

# Get formatted message history
def get_formatted_message_history(message_history, user_id):
    user_id = str(user_id)
    return message_history.get(user_id, [])

