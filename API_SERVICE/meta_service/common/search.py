from meta_service.ELKSearch.Utils.base import set_els
from meta_service.ELKSearch.document import DocumentManager


def default_search_set(server_config, index, size=10, from_=0):
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


