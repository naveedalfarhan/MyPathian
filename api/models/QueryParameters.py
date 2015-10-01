class QueryParameters:
    take = 10
    skip = 0
    page = 0
    sort = []
    filter = None
    start_date = None
    end_date = None

    def __init__(self, p=None):
        if p is not None:
            if "take" in p:
                self.take = int(p["take"])
            if "skip" in p:
                self.skip = int(p["skip"])
            if "page" in p:
                self.page = int(p["page"])
            if "sort" in p:
                self.sort = p["sort"]
            if "filter" in p:
                self.filter = p["filter"]
            if 'start_date' in p:
                self.start_date = int(p['start_date'])
            if 'end_date' in p:
                self.end_date = int(p['end_date'])


class QueryResult:
    def __init__(self, data=None, total=None):
        self.data = data
        self.total = total

    def to_dict(self):
        return dict(data=self.data, total=self.total)