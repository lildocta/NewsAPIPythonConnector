class Article:
    def __init__(self, title, description, url, source, date):
        self.title = title or u'None'
        self.description = description or u'None'
        self.url = url or u'None'
        self.source = source or u'None'
        self.date = date or u'None'