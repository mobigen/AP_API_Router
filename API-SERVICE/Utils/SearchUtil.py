from ELKSearch.Utils.elasticsearch_utils import make_query


def data_srttn_index(item_dict):
    """
    검색 데이터의 카운팅을 위한 함수
    :param item_dict:
    :return:
    """
    for i, item in enumerate(item_dict["filter"]):
        if "data_srttn" in item["match"].keys():
            return i
        else:
            return None


def search_count(es, item_dict, query_dict):
    index = "biz_meta,v_biz_meta_oversea_els"
    data_dict = dict()
    data_srttn = {
        # search_keyword: (result_key, result_data)
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount",
        "전체": "totalCount",
    }

    i = data_srttn_index(item_dict)

    for ko_nm, eng_nm in data_srttn.items():
        if i is None:
            cnt_query = make_query(
                "match", "data_srttn", {"operator": "OR", "query": ko_nm}
            )
            item_dict["filter"].append(cnt_query)
            i = -1
        else:
            item_dict["filter"][i]["match"]["data_srttn"]["query"] = ko_nm

        if ko_nm == "전체":
            del item_dict["filter"][i]

        query_dict.update(item_dict)
        cnt_query = make_query("query", "bool", query_dict)
        cnt = es.conn.count(index=index, body=cnt_query)["count"]
        data_dict[eng_nm] = cnt

    return data_dict


def ckan_query(search_option) -> dict:
    """
    2023-10-20 변경사항
    ckan_data 사용X
     해외데이터 외부데이터는 v_biz_meta_oversea_els 통합
    :param search_option:
    :return:
    """
    search_format = "(*{0}*)"
    query_dict = []

    for query in search_option:
        keywords = [search_format.format(word) for keyword in query.keywords for word in keyword.split(" ")]
        if len(keywords) > 1:
            keywords = f" {query.operator.upper()} ".join(keywords)
        else:
            keywords = keywords[0]
        query_dict.append({"query_string": {"query": keywords,"fields": query.field}})

    return {"must": query_dict}
