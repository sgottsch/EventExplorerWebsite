from urllib.parse import urlparse


class Document:

    def __init__(self, document_id, title, snippet, date, archive_url=None, live_url=None):
        self.domain = None
        self.live_url = None
        title = title.strip()
        snippet = snippet.strip()
        self.id = document_id
        self.title = title
        self.archive_url = archive_url
        # if snippet != title:
        self.snippet = snippet
        self.date = date
        self.set_live_url(live_url)

    def set_live_url(self, live_url):
        self.live_url = live_url
        self.domain = urlparse(live_url).netloc
