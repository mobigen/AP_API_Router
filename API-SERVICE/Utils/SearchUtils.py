from ELKSearch.Utils.elasticsearch_utils import  make_query


def search_count(es, item_dict, query_dict):
    data_dict = dict()
    data_srttn = {
        # search_keyword: (result_key, result_data)
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount",
        "전체": "totalCount",
    }

    # ############ data_srttn ############
    i = None
    for j, item in enumerate(item_dict["filter"]):
        if "data_srttn" in item["match"].keys():
            i = j
            break
        else:
            i = None

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
        cnt = es.conn.count(index=es.index, body=cnt_query)["count"]
        data_dict[eng_nm] = cnt

    return data_dict