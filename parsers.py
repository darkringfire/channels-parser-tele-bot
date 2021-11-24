from pathlib import Path
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeFilename, Message


def get_post_group(post):
    """

    :type post: Post | None
    :rtype: int | None
    """
    if post is None:
        return None
    return post.group


class Post:
    def __init__(self, ch_id, msg=None):
        """
        Create post and optional add message

        :param Message | None msg: Message to add
        :type ch_id: int
        """
        self.ch_id = ch_id
        self.id = None
        self.post_name = None
        self.group = None
        self.texts = []
        self.docs = []
        self.photos = []
        if msg is not None:
            self.add_msg(msg)

    def is_text(self):
        return len(self.texts) > 0 and len(self.docs) == 0 and len(self.photos) == 0

    def is_docs(self):
        return len(self.texts) == 0 and len(self.docs) > 0 and len(self.photos) == 0

    def is_photos(self):
        return len(self.texts) == 0 and len(self.docs) == 0 and len(self.photos) > 0

    def add_msg(self, msg):
        """

        :type msg: Message
        """
        self.group = msg.grouped_id
        media = msg.media
        if msg.grouped_id is None:
            self.id = msg.id
        else:
            self.id = msg.grouped_id
        if media is None:
            self.texts.append(msg.message)
        elif isinstance(media, MessageMediaPhoto):
            self.photos.append(msg)
        elif isinstance(media, MessageMediaDocument):
            self.docs.append(msg)

    def print(self):
        print('== POST ==')
        print('TEXTS  :', self.texts)
        print('DOCS   :', self.docs)
        print('PHOTOS :', self.photos)

    async def download(self, dl_dir):
        """

        :type dl_dir: str | Path
        """
        post_name = self.post_name
        if post_name is None:
            post_name = '{}-{}'.format(self.ch_id, self.id)
        subdir = Path(dl_dir)
        content_count = len(self.docs) + len(self.photos)
        if content_count > 1:
            subdir = subdir.joinpath(post_name)
            subdir.mkdir(parents=True, exist_ok=True)

        for n, text in enumerate(self.texts):
            name = '{}-{:0>2d}'.format(post_name, n)
            text_file = subdir.joinpath(name).with_suffix('.txt')
            print('TEXT  to "{}"'.format(text_file))
            with text_file.open('w') as f:
                f.write(text)
        for doc in self.docs:
            name = ''
            for a in doc.media.document.attributes:
                if isinstance(a, DocumentAttributeFilename):
                    name = a.file_name
            doc_file = subdir.joinpath(name)
            print('DOC   to "{}"'.format(doc_file))
            await doc.download_media(doc_file)

        for n, photo in enumerate(self.photos):
            name = '{}-{:0>2d}'.format(post_name, n)
            photo_file = subdir.joinpath(name).with_suffix('.jpg')
            print('PHOTO to "{}"'.format(photo_file))
            await photo.download_media(photo_file)


class ParserBase:
    posts: list[Post]

    def __init__(self, parser_id):
        """

        :type parser_id: int
        """
        self.posts = []
        self.complex_posts = []
        self.id = parser_id

    def print_posts(self):
        for p in self.posts:
            p.print()

    def add_msg(self, msg):
        """
        Add message to parser posts storage

        :param Message msg: Message to add
        """
        if self.is_new_post_msg(msg):
            self.posts.append(Post(self.id, msg))
        else:
            self.get_last_post().add_msg(msg)

        if self.is_complex():
            last_complex_group = get_post_group(self.get_last_complex_post())
            if msg.grouped_id is None or last_complex_group != msg.grouped_id:
                self.complex_posts.append(Post(self.id))
                # self.complex_posts.append(Post(self.id, msg))
            last_complex_post = self.get_last_complex_post()
            last_complex_post.texts = []
            last_complex_post.docs = []
            last_complex_post.photos = []
            for post in self.get_posts_to_complex():
                last_complex_post.group = post.group
                last_complex_post.texts += post.texts
                last_complex_post.docs += post.docs
                last_complex_post.photos += post.photos

    def get_last_post(self):
        """

        :rtype: Post | None
        """
        if len(self.posts) == 0:
            return None
        return self.posts[-1]

    def get_last_complex_post(self):
        """

        :rtype: Post | None
        """
        if len(self.complex_posts) == 0:
            return None
        return self.complex_posts[-1]

    def is_new_post_msg(self, msg):
        """

        :type msg: Message
        """
        last_group = get_post_group(self.get_last_post())
        new_group = msg.grouped_id
        return last_group is None or new_group is None or last_group != new_group

    def is_complex(self):
        return len(self.posts) > 0

    def get_posts_to_complex(self):
        """

        :rtype: list[Post] | None
        """
        if self.is_complex():
            return self.posts[-1:]
        return None

    async def download(self, dl_dir):
        """

        :type dl_dir: str | Path
        """
        for post in self.posts:
            await post.download(dl_dir)


class ParserFonts(ParserBase):
    def __init__(self, parser_id):
        ParserBase.__init__(self, parser_id)

    def add_msg(self, msg):
        ParserBase.add_msg(self, msg)
        last_complex_post = self.get_last_complex_post()
        if last_complex_post is not None:
            name = ''
            for a in last_complex_post.docs[0].media.document.attributes:
                if isinstance(a, DocumentAttributeFilename):
                    name = Path(a.file_name).stem

            last_complex_post.post_name = name

    def get_posts_to_complex(self):
        """

        :rtype: list[Post] | None
        """
        if self.is_complex():
            return self.posts[-3:]
        return None

    def is_complex(self):
        if len(self.posts) >= 3:
            if self.posts[-1].is_photos() and self.posts[-2].is_text() and self.posts[-3].is_docs():
                return True
        return False

    def print_posts(self):
        for p in self.complex_posts:
            p.print()

    async def download(self, dl_dir):
        for post in self.complex_posts:
            await post.download(dl_dir)
