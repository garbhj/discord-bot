import os
import google.generativeai as genai
from google.api_core import retry
from PIL import Image
import io


# Load the Google AI key from environment variables
GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")
genai.configure(api_key=GOOGLE_AI_KEY)

text_generation_config = genai.GenerationConfig(
    temperature=0.7,
    top_p=1,
    top_k=1,
    max_output_tokens=4096,
)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

main_model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=text_generation_config,
                                   safety_settings=safety_settings)
backup_model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=text_generation_config,
                                    safety_settings=safety_settings)

async def generate_response_with_text(message_text):
    prompt_parts = [message_text]
    response = main_model.generate_content(prompt_parts)
    if response._error:
        return "❌" + str(response._error)
    return response.text

async def generate_response_with_image_and_text(image_data, text):
    image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
    prompt_parts = [image_parts[0], f"\n{text if text else 'What is this a picture of?'}"]
    response = main_model.generate_content(prompt_parts)
    if response._error:
        return "❌" + str(response._error)
    return response.text

# To handle multiple attachements
async def generate_multimodal_response(text, attachments):
    prompt_parts = [text] if text else ["Please respond to these files, as you deem appropriate."]

    for attachment in attachments:
        if 'image' in attachment['mime_type']:
            image = Image.open(io.BytesIO(attachment['data']))
            prompt_parts.append(image)
        elif 'audio' in attachment['mime_type']:
            if attachment['upload_type'] == 'inline':
                prompt_parts.append({
                    'mime_type': attachment['mime_type'],
                    'data': attachment['data']
                })
            elif attachment['upload_type'] == 'file_api':
                # file = genai.get_file(attachment['data'])
                prompt_parts.append(attachment['data'])  # 


    # I added these print statements for troubleshooting
    print(len(prompt_parts))

    print("Generating content...")
    response = backup_model.generate_content(prompt_parts)
    print("Finished!!!", "\n", response)
    
    if response._error:
        print(str(response._error))
        return "❌" + str(response._error)
    print(response.text)
    return response.text
