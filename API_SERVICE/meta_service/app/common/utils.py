import re


def data_process(data):
    for k, v in data.items():
        if not v:
            continue

        if k in ["re_ctgry", "re_data_shap", "re_data_prv_desk"]:
            data[k] = re.sub("[ ]", "", str(v))

        if isinstance(v, str):
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.(\d+)", v)
            if match:
                date_time_field = match.group(1).replace(" ", "T")
                micro_time_field = match.group(2)

                if "+" in micro_time_field:
                    micro_time_field = micro_time_field.split("+")[0]
                    if len(micro_time_field) < 6:
                        micro_time_field = micro_time_field + "0"

                data[k] = f"{date_time_field}.{micro_time_field}"

    return {"_id": data["biz_dataset_id"], "_source": data}
