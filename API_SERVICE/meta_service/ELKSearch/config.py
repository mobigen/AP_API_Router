from meta_service.ELKSearch.model import ElsServerConfig
"""
검색에 사용할 설정을 정의
local_els와 비슷한 양식으로 정의

ex)
변수명 = ElsServerConfig(
    "els 주소",
    "els 포트"
)
"""

local_server = ElsServerConfig(
    host="0.0.0.0",
    port="9200"
)
