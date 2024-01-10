import re
from copy import deepcopy

from batch_service.app.ELKSearch.Utils.base import set_els
from batch_service.app.ELKSearch.document import DocumentManager
from batch_service.app.ELKSearch.index import Index


def default_search_set(host, port, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(host, port)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def index_set(host, port):
    es = set_els(host, port)
    return Index(es)


def data_process(data):
    pre_data = deepcopy(data)
    for k, v in data.items():
        if not v:
            continue

        if k in ["ctgry", "data_shap", "data_prv_desk"]:
            key = f"re_{k}"
            pre_data[key] = re.sub("[ ]", "", str(v))

        if isinstance(v, str):
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.(\d+)", v)
            if match:
                date_time_field = match.group(1).replace(" ", "T")
                micro_time_field = match.group(2)

                if "+" in micro_time_field:
                    micro_time_field = micro_time_field.split("+")[0]
                    if len(micro_time_field) < 6:
                        micro_time_field = micro_time_field + "0"

                pre_data[k] = f"{date_time_field}.{micro_time_field}"

    return {"_id": pre_data["biz_dataset_id"], "_source": pre_data}
