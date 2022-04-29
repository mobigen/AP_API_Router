import logging
from typing import List, Dict

#logger = logging.getLogger()


def convert_data(data) -> str:
    return f'\'{str(data)}\''


def make_table_info_query(db: str, table: str) -> str:
    sql = f'SELECT * FROM information_schema.columns WHERE table_schema = {convert_data(db)} AND table_name = {convert_data(table)}'
    return sql


def make_insert_query(table: str, into_info: List[Dict]) -> str:
    columns = into_info[0].keys()
    values = [
        f'( {",".join(map(convert_data, info.values()))} )' for info in into_info]
    sql = f'INSERT INTO {table} ( {",".join(columns)} ) VALUES {",".join(values)};'
    return sql


def make_update_query(table: str, set_info: Dict, where_info: Dict) -> str:
    set_list = [
        f'{column} = {convert_data(value)}' for column, value in set_info.items()]
    where_list = [
        f'{column} = {convert_data(value)}' for column, value in where_info.items()]
    sql = f'UPDATE {table} SET {",".join(set_list)} WHERE {",".join(where_list)};'
    return sql


def make_delete_query(table, where_info: Dict) -> str:
    where_list = [
        f'{column} = {convert_data(value)}' for column, value in where_info.items()]
    sql = f'DELETE FROM {table} WHERE {",".join(where_list)};'
    return sql


