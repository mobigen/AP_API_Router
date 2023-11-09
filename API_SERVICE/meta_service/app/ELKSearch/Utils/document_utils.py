

def search_filter(find_data):
    return [data["_source"] for data in find_data["hits"]["hits"]]


def set_source(source):
    if source is None:
        return []
    else:
        return source
