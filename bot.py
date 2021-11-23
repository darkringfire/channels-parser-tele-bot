import pathlib

from telethon import TelegramClient

from conf import *


async def download_post(post):
    await post['file'].download_media(
        file=pathlib
        .Path(post['name'])
        .joinpath(post['file'].media.document.attributes[0].file_name)
    )
    for i, pic in enumerate(post['photos']):
        await pic.download_media(
            file=pathlib
            .Path(post['name'])
            .joinpath('{}-{:0>2d}.jpg'.format(post['name'], i) + '.jpg')
        )


async def bot(client):
    for ch_id in channels.keys():
        post = {
            'name': None,
            'file': None,
            'photos': [],
        }
        ch_seq = channels[ch_id]
        seq_n = -1
        prev_grouped_id = None
        async for message in client.iter_messages(ch_id, limit=msg_lim):
            if message.grouped_id is None:
                seq_n += 1
            elif message.grouped_id != prev_grouped_id:
                seq_n += 1
            prev_grouped_id = message.grouped_id
            if seq_n >= len(ch_seq):
                await download_post(post)
                seq_n = 0

            if seq_n == 0:
                post = {
                    'name': None,
                    'file': None,
                    'photos': [],
                }

            # print('----------------')
            ch_seq_n = ch_seq[seq_n]
            msg_format = ch_seq_n['format']
            msg_match = True
            for key, val in msg_format.items():
                # print(key, val)
                attr = getattr(message, key)
                # print(key, '=', attr)
                # print('check', val)
                if val[0] is None:
                    if attr is not None:
                        msg_match = False
                elif not isinstance(attr, val[0]):
                    msg_match = False
                elif val[1] is not None and val[1] != attr:
                    msg_match = False
            # print(msg_match)
            if msg_match:
                if ch_seq_n['save_name']:
                    post['name'] = pathlib.Path(message.media.document.attributes[0].file_name).stem
                if ch_seq_n['save']:
                    if isinstance(message.media, MessageMediaDocument):
                        # post['file'] = message.media.document.id
                        post['file'] = message
                    elif isinstance(message.media, MessageMediaPhoto):
                        # post['photos'].append(message.media.photo.id)
                        post['photos'].append(message)
        if post['name'] is not None:
            await download_post(post)
            # print('id=', message.id)
            # print('message=', message.message)
            # print('media=', message.media)
            # print('grouped_id=', message.grouped_id)


def main():
    with TelegramClient('parser-bot', api_id, api_hash) as client:
        client.loop.run_until_complete(bot(client))


main()
