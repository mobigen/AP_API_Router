from typing import Dict, List
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class addTableColumn(BaseModel):
    table_nm: str
    eng_nm: str
    kor_nm: str
    data_type: str


# column_type : number | string | time | auto_index
# constraint : primary key, unique, not null
'''
abstime : 절대 날짜와 시간
aclitem : 엑세스 제어 목록 아이템
bool : 부울런(논리) 값
box : 2차원 사각형
bytea : 가변길이의 바이트 배열
bpchar : 공백 채움 문자
char : 문자
char2 : 2 문자의 배열
char4 : 4 문자의 배열
char8 : 8문자의 배열
char16 : 16문자의 배열
cid : 명령 식별 타입
date : ANSI SQL 데이터 타입
datetime : 범용 날짜와 시간
filename : 거대 객체의 파일이름
int2 : 부호있는 2바이트 정수
int28 : int2의 8 배열
int4 : 부호있는 2바이트 정수
float4 : 단정도 부동소수
float8 : 배정도 부동소수
lseg : 2차원 선 구간
money : 고정 정밀도를 가지는 십진수 타입
name : 저장 시스템 식별자를 위한 다중 문자 타입
oid : 객체 식별자 타입
oid8 : oid의 8 배열 
oidint2 : oid 와 int2의 조합
oidint4 : oid 와 int4의 조합 
oidchar16 : oid 와 char16의 조합
path : 열렸거나 닫혀진 선 구간 
point : 2차원 기하학 점
polygon : 2차원 다각형 (닫혀진 path와 동일)
circle : 2차원 원 (중심점과 반경)
regproc : 등록된 프로시저
reltime : 상대 날짜와 시간 간격
smgr : 저장 관리자
text : 가변길이의 문자 배열
tid : 튜플 식별자 타입
time : ANSI SQL 시간 타입
timespan : 범용 시간 간격
timestemp : 제한 범위 ISO형식의 날짜와 시간 
tinterval : 시간 간격(절대시작시각과 절대종료시각)
varchar : 가변길이의 문자들
xid : 트랜잭션 식별자 타입
'''


def get_type(data_type, length=None):
    if data_type == "number":
        column_type = "int4"
    elif data_type == "string":
        if length:
            column_type = f'varchar({length})'
        else:
            column_type = "varchar"
    elif data_type == "time":
        column_type = "timestamp"
    else:
        raise Exception(f"Invalid type ({data_type})")
    return column_type


def api(add_table_columns: List[addTableColumn]) -> Dict:
    try:
        db = connect_db(config.db_info)

        for add_table_column in add_table_columns:
            table_name = add_table_column.table_nm.lower()

            add_column_query = f'ALTER TABLE {table_name} ADD {add_table_column.eng_nm} {add_table_column.data_type};'
            db.execute(add_column_query)

            get_table_id_query = f'SELECT id FROM tb_table_list WHERE table_nm = {convert_data(table_name)};'
            result, _ = db.select(get_table_id_query)
            table_id = result[0]["id"]
            column_info_query = f'INSERT INTO tb_table_column_info (table_id, kor_nm, eng_nm) \
                                        VALUES ({convert_data(table_id)}, \
                                                {convert_data(add_table_column.kor_nm)}, \
                                                {convert_data(add_table_column.eng_nm)});'
            db.execute(column_info_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
