import json
import os
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import shutil

# Replace these with your own values
api_id = "API_ID"  # Your API ID
api_hash = 'API_HASH'  # Your API hash
phone_number = 'PHONE_NUMBER'  # Your phone number with country code

client = TelegramClient('session_name', api_id, api_hash)

def get_post(channel_name, message_id):
    # Get the channel entity
    channel = client.get_entity(channel_name)
    channel_title = channel.title

    # Fetch the channel's profile photo
    channel_photo = None
    if channel.photo:
        channel_photo = client.download_profile_photo(channel, file=f"channel_{channel.id}.jpg")

    # Fetch the message with the given ID
    message = client.get_messages(channel, ids=message_id)
    if not message:
        print(f"Message ID {message_id} not found in channel {channel_name}")
        return None

    # Process the message data
    message_data = {
        'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
        'channel_name': channel_title,
        'channel_photo': channel_photo,
        'message_id': message.id,
        'forwarded_from': None,
        'reactions': {},
        'views': message.views or -1,
        'text': message.text or '',
        'media_files': [],  # List of tuples (media_type, filename)
    }

    # Handle forwarded messages
    if message.forward:
        if message.forward.sender:
            message_data['forwarded_from'] = getattr(message.forward.sender, 'username', None) \
                                             or getattr(message.forward.sender, 'title', None)
        elif message.forward.chat:
            message_data['forwarded_from'] = message.forward.chat.title
        else:
            message_data['forwarded_from'] = 'Unknown'

    # Handle reactions
    if message.reactions:
        reactions = {}
        for reaction in message.reactions.results:
            emoji = reaction.reaction.emoticon
            reactions[emoji] = reaction.count
        message_data['reactions'] = reactions

    # Download media if any
    if message.media:
        # Create a directory for the message
        message_dir = f"message_{message_id}"
        os.makedirs(message_dir, exist_ok=True)

        if message.grouped_id:
            # Fetch all messages in the media group (album)
            media_messages = client.get_messages(channel, ids=list(range(message_id, message_id + 10)))
            for m in media_messages:
                if m.grouped_id == message.grouped_id and m.media:
                    process_media(m, message_data, message_dir)
        else:
            process_media(message, message_data, message_dir)

    return message_data

def process_media(message, message_data, message_dir):
    if isinstance(message.media, MessageMediaPhoto):
        file_path = message.download_media(file=message_dir)
        if file_path:
            media_filename = os.path.basename(file_path)
            message_data['media_files'].append(('image', media_filename))
    elif isinstance(message.media, MessageMediaDocument):
        if message.file.mime_type.startswith('video'):
            # Download video
            file_path = message.download_media(file=message_dir)
            if file_path:
                media_filename = os.path.basename(file_path)
                message_data['media_files'].append(('video', media_filename))
        elif message.file.mime_type.startswith('image'):
            file_path = message.download_media(file=message_dir)
            if file_path:
                media_filename = os.path.basename(file_path)
                message_data['media_files'].append(('image', media_filename))
        else:
            # Other types (e.g., documents), handle if needed
            pass

def create_html(message_data):
    # Create a directory for the message files
    message_dir = f"message_{message_data['message_id']}"
    os.makedirs(message_dir, exist_ok=True)

    # Copy channel photo to message directory
    if message_data['channel_photo']:
        channel_photo_filename = os.path.basename(message_data['channel_photo'])
        shutil.copy(message_data['channel_photo'], os.path.join(message_dir, channel_photo_filename))
    else:
        channel_photo_filename = None

    # Generate the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Telegram Post</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #ffffff;
                padding: 20px;
                margin: 0;
                overflow: hidden;
            }}
            .message {{
                border: 1px solid #e5e5e5;
                border-radius: 10px;
                padding: 15px;
                max-width: 600px;
                margin: auto;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .message-header {{
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }}
            .channel-icon {{
                width: 46px;
                height: 46px;
                border-radius: 50%;
                background-color: #8a99a6;
                margin-right: 12px;
                overflow: hidden;
            }}
            .channel-icon img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .channel-name {{
                font-weight: bold;
                font-size: 16px;
                color: #000;
            }}
            .message-date {{
                color: #808991;
                font-size: 13px;
            }}
            .message-text {{
                font-size: 15px;
                line-height: 1.5;
                color: #000;
                margin-bottom: 12px;
            }}
            .message-media img, .message-media video {{
                max-width: 100%;
                border-radius: 8px;
                margin-bottom: 12px;
            }}
            .message-media video {{
                outline: none;
            }}
            .message-footer {{
                display: flex;
                justify-content: space-between;
                color: #808991;
                font-size: 14px;
            }}
            .reactions {{
                display: flex;
                gap: 8px;
            }}
            .reaction {{
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            ::-webkit-scrollbar {{
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="message">
            <div class="message-header">
                <div class="channel-icon">
    """

    # Add the channel photo if available
    if channel_photo_filename:
        html_content += f'<img src="{channel_photo_filename}" alt="Channel Icon">'
    else:
        html_content += f'<img src="https://via.placeholder.com/46" alt="Channel Icon">'

    html_content += f"""
                </div>
                <div>
                    <div class="channel-name">{message_data['channel_name']}</div>
                    <div class="message-date">{message_data['date']}</div>
                </div>
            </div>
            <div class="message-text">
                {message_data['text'].replace('\n', '<br>')}
            </div>
    """

    # Add media if any
    if message_data['media_files']:
        html_content += '<div class="message-media">'
        for media_type, media_file in message_data['media_files']:
            if media_type == 'image':
                html_content += f'<img src="{media_file}" alt="Media">'
            elif media_type == 'video':
                html_content += f'''
                <video controls>
                    <source src="{media_file}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                '''
        html_content += '</div>'

    # Add reactions if any
    if message_data['reactions']:
        reactions_html = ''.join([f'<div class="reaction">{emoji} {count}</div>' for emoji, count in message_data['reactions'].items()])
        reactions_html = f'<div class="reactions">{reactions_html}</div>'
    else:
        reactions_html = ''

    # Footer with views and reactions
    html_content += f"""
            <div class="message-footer">
                <div>👁 {message_data['views']}</div>
                {reactions_html}
            </div>
        </div>
    </body>
    </html>
    """

    # Save the HTML file in the message directory
    html_filename = os.path.join(f"message_{message_data['message_id']}", f"message_{message_data['message_id']}.html")
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_filename

def render_html_to_image(html_filename, output_image):
    from selenium.webdriver.common.by import By

    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Set a high window size to accommodate large content
    chrome_options.add_argument("--window-size=1920,10800")  # Width x Height
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--force-device-scale-factor=1")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the HTML file
        file_url = 'file://' + os.path.abspath(html_filename)
        driver.get(file_url)

        # Wait for the page to load
        time.sleep(2)

        # Find the message element
        message_element = driver.find_element(By.CLASS_NAME, 'message')

        # Get the size of the element
        element_width = message_element.size['width']
        element_height = message_element.size['height']

        # Set the window size to match the element size
        driver.set_window_size(element_width, element_height + 100)  # Add extra height if needed

        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", message_element)

        # Wait for any scrolling to finish
        time.sleep(0.5)

        # Take a screenshot of the element
        message_element.screenshot(output_image)
        print(f"Screenshot saved to {output_image}")

    finally:
        driver.quit()



if __name__ == '__main__':
    # Start the client
    client.start()
    print("Client Created")

    # Ensure you're authorized
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        try:
            client.sign_in(phone_number, input('Enter the code sent to your Telegram: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Password: '))

    # Example usage of get_post
    channel_name = "Солома INFO - Солом'янський район"  # Replace with the actual channel username
    message_id = 3851  # Replace with the actual message ID

    message_data = get_post(channel_name, message_id)
    if message_data:
        print(json.dumps(message_data, indent=4, ensure_ascii=False))
        html_filename = create_html(message_data)
        output_image = os.path.join(os.path.dirname(html_filename), f"post_{message_id}.png")
        render_html_to_image(html_filename, output_image)
    else:
        print("Message not found.")
