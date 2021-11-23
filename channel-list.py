# Scrip prints all subscriptions to Channels
# If client not authorized, script requests phone and auth code

from telethon import TelegramClient
from telethon.tl.types import Channel

from conf import *


async def bot(client):
    # Check all dialogs and select Channels only:
    async for dialog in client.iter_dialogs():
        if isinstance(dialog.entity, Channel):
            print(dialog.id, dialog.name)


def main():
    with TelegramClient('parser-bot', api_id, api_hash) as client:
        client.loop.run_until_complete(bot(client))


main()
