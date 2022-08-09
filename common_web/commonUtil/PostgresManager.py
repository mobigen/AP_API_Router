import psycopg2


class PostgresManager:
    def __init__(self, host: str, port: str, user: str, password: str, database: str, schema: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        conn = psycopg2.connect(host=self.host, port=self.port, user=self.user,
                                password=self.password, database=self.database,
                                options=f"-c search_path={self.schema}")
        print("PostgresManager Connect.")
        return conn

    def execute(self, sql: str) -> None:
        self.cursor.execute(sql)
        self.conn.commit()
        print(f'PostgresManager Execute Result. ({sql})')

    def commit(self):
        self.conn.commit()

    def __del__(self) -> None:
        print("DB Close")
        self.cursor.close()
        self.conn.close()
