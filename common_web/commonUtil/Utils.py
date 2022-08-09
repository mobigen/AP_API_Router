from .PostgresManager import PostgresManager


def connect_db(db_info):
    db = PostgresManager(host=db_info["host"], port=db_info["port"],
                         user=db_info["user"], password=db_info["password"],
                         database=db_info["database"], schema=db_info["schema"])
    return db
