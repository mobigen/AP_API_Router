from typing import Dict
from datetime import datetime
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ELKSearch.Utils.database_utils import get_config
from Utils.CommonUtil import get_exception_info
from Utils.SearchUtil import search_count, ckan_query
from ApiService.ApiServiceConfig import config


def api(input: InputModel) -> Dict:
    """
    2023-10-20 변경사항
    ckan_data 사용X
    해외데이터 외부데이터는 v_biz_meta_oversea_els 통합
    :param search_option:
    :return:
    """
    from_ = input.from_ - 1
    els_config = get_config(config.root_path, "config.ini")[config.db_type[:-3]]
    index = "ckan_data"
    try:
        if input.chk and len(input.searchOption):
            with open(
                    f"{config.root_path}/log/{config.category}/{datetime.today().strftime('%Y%m%d')}_search.log",
                    "a",
            ) as fp:
                for search in input.searchOption:
                    fp.write(f"{str(search.keywords)}\n")

        es = ElasticSearchManager(page=from_, size=input.size, index=index, **els_config)
        es.set_sort(input.sortOption)

        ############ search option ############
        query_dict = ckan_query(input.searchOption)
        search_query = make_query("query","bool", query_dict)
        es.body.update(search_query)

        # ############ sort option ############
        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

        data_dict = search_count(es, {'filter': []}, query_dict)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in search_data["hits"]["hits"]]
        data_dict["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
