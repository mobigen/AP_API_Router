from meta_service.ELKSearch.Utils.base import set_els
from meta_service.ELKSearch.document import DocumentManager


def common_prefix(server_config, index, size, prefix_model):
    query = {prefix_model.col_nm: prefix_model.keyword}
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size=size)
    return docmanger.prefix(body=query)
