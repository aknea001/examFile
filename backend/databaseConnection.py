from mysql.connector import pooling, Error as mysqlError
from dotenv import load_dotenv
from os import getenv

class Database():
    def __init__(self):
        load_dotenv()

        self.dbConfig = {
            "host": getenv("sqlhost"),
            "user": getenv("sqluser"),
            "password": getenv("sqlpasswd"),
            "database": getenv("sqldb")
        }

        self.pool = pooling.MySQLConnectionPool (
            pool_name = "mypool",
            pool_size = 5,
            **self.dbConfig
        )
    
    def execute(self, query: str, *args, **kw: int):
        values = tuple(args)
        amount = kw.get("a", 1)

        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(buffered=True)

            cursor.execute(query, values)

            if query.upper().startswith("SELECT"):
                data = cursor.fetchone() if amount <= 1 else cursor.fetchall()

                return data
            
            connection.commit()
        except mysqlError as e:
            raise ConnectionError(e)
        finally:
            cursor.close()
            connection.close()