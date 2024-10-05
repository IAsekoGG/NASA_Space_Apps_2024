import json
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from datetime import datetime, timedelta
from tqdm import tqdm


# Replace these with your own values
api_id = 25835755           # integer value, e.g., 1234567
api_hash = '3c56d1bdd1e114bb582379c9f865c74f'     # string value, e.g., '0123456789abcdef0123456789abcdef'
phone_number = '+380635247972'   # Your phone number with country code, e.g., '+1234567890'

channels_username = ['kpi_hostel18', 'kpi_hostel4', 'kpi_hostel7', 'kpi_hostel19', 'kpi_hostel16', 'kpi_hostel14', 'kpi_hostel8', 'kpi_hostel20', 'soloma_info_kyiv']  # e.g., 'example_channel'

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Start the client
    await client.start()
    print("Client Created")

    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        try:
            await client.sign_in(phone_number, input('Enter the code sent to your Telegram: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    # Replace 'channel_username' with the username or ID of the channel

    # Get the channel entity
    for channel_username in channels_username:
        channel = await client.get_entity(channel_username)
        channel_name = channel.title

        messages_data = []

        one_year_ago = datetime.utcnow() - timedelta(days=365)
        loop = tqdm()

        # Iterate over messages
        async for message in client.iter_messages(channel, reverse=True, offset_date=one_year_ago):
            try:
                message_data = {
                    'date': message.date.isoformat(),
                    'channel_name': channel_name,
                    'message_id': message.id,
                    'forwarded_from': None,
                    'reactions': {},
                    'views': message.views or -1,
                    'text': message.text,
                    'comments': [],
                }
                loop.set_postfix({'date': message.date.isoformat(), 'channel_name': channel_name})
                loop.update(1)


                # Forwarded from
                if message.forward:
                    if message.forward.sender:
                        message_data['forwarded_from'] = getattr(message.forward.sender, 'username', None) or getattr(message.forward.sender, 'title', None)
                    elif message.forward.chat:
                        message_data['forwarded_from'] = message.forward.chat.title
                    else:
                        message_data['forwarded_from'] = 'Unknown'

                # Reactions
                if message.reactions:
                    reactions = {}
                    for reaction in message.reactions.results:
                        emoji = reaction.reaction.emoticon
                        reactions[emoji] = reaction.count
                    message_data['reactions'] = reactions

                # Comments (Replies)
                if message.replies:
                    async for reply in client.iter_messages(channel, reply_to=message.id, reverse=True):
                        reply_data = {
                            'date': reply.date.isoformat(),
                            'message_id': reply.id,
                            'text': reply.text,
                            'reactions': {}
                        }

                        # Reactions to the reply
                        if reply.reactions:
                            reply_reactions = {}
                            for reaction in reply.reactions.results:
                                emoji = reaction.reaction.emoticon
                                reply_reactions[emoji] = reaction.count
                            reply_data['reactions'] = reply_reactions

                        message_data['comments'].append(reply_data)

                messages_data.append(message_data)
            except Exception as e:
                print(e)

        # Output to JSON file
        with open(f'{channel_name}.json', 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=4)

# Run the client
with client:
    client.loop.run_until_complete(main())

