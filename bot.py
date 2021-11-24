from telethon import TelegramClient

from conf import *


async def bot(client):
    for ch_id, parser_class in channels.items():
        parser = parser_class(ch_id)
        async for message in client.iter_messages(ch_id, limit=msg_lim):
            parser.add_msg(message)
        # parser.print_posts()
        await parser.download('ex')


def main():
    with TelegramClient('parser-bot', api_id, api_hash) as client:
        client.loop.run_until_complete(bot(client))


main()
