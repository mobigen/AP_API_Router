import os
import uuid
import sqlalchemy
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from ELKSearch.Utils.database_utils import prepare_config
# root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
# prepare_config(root_path)


def get_table(table_name,session):
    return sqlalchemy.Table(table_name,sqlalchemy.MetaData(),autoload=True,autoload_with=session.get_bind())


"""
d-ocean sample data 입력

[default 값]
p.key = 기타
datatype = 기본
src_sys = d-ocean (전부 대문자로 치환)
data_upd_cycle = M

[ID 값으로 변환]
kywrd = 텍스트로 그냥 입력
ctgry - meta_change_ctgry_dtl
prv_forml - biz_meta_fltr_bas
src_sys - biz_meta_fltr_bas

"""
insert_db = create_engine(f"postgresql://dpme:hello.meta12#$@192.168.100.126:25432/ktportal",
                   connect_args={'options': '-csearch_path=meta'})

# insert_db = create_engine(f"postgresql://postgres:0312@localhost:5432/ktportal",
#                    connect_args={'options': '-csearch_path=meta'})

sess = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=insert_db))
base = declarative_base()

data = pd.DataFrame(pd.read_excel("./d-ocean_sample.xlsx"))
print(data.head())
print(data.columns)

####### 샘플 데이터 수정 #######


####### 데이터 DB INSERT #######
table_name = "test"
table_name = table_name.lower()


data.columns = [col.lower() for col in list(data.columns)]
table = get_table(table_name,sess)
columns = table.columns.keys()

data = data.replace('', None)
for col in list(data.columns):
    data[col] = data[col].astype(str)
    if col not in columns:
        sess.execute('ALTER TABLE {} ADD {} TEXT'.format(table_name, col))

del data["bm"]
del data["pkey"]
del data["datatype"]
data["biz_dataset_id"] = [uuid.uuid4() for i in range(0,len(data))]

with insert_db.connect() as conn:
    data.to_sql(table_name,con=conn,if_exists='replace', index=False, index_label=False)
