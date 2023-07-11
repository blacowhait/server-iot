import asyncpg
from settings import get_settings
from functools import lru_cache

settings = get_settings()
class Database:
    def __init__(self):
        self.user = settings.DB_USERNAME
        self.password = settings.DB_PASSWORD
        self.host = settings.DB_HOST
        self.port = settings.DB_PORT
        self.database = settings.DB_NAME
        self._cursor = None

        self._connection_pool = None
        self.con = None

    async def jsonify(self, records):
        """
        Parse asyncpg record response into JSON format
        """
        list_return = []
        for r in records:
            itens = r.items()
            list_return.append({i[0]: i[1].rstrip() if type(
                i[1]) == str else i[1] for i in itens})
        return list_return

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=20,
                    max_size=20,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )

            except Exception as e:
                print(e)

    async def fetch_rows(self, query: str):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                print("Success for", query)
                # return result
                return await self.jsonify(result)
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)

    async def fetch_rows_no_json(self, query: str):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                print("Success for", query)
                return result
                # return await self.jsonify(result)
            except Exception as e:
                return e
            finally:
                await self._connection_pool.release(self.con)

    async def execute(self, query: str):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.execute(query)
                print("Results", result)
                return result
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)

    async def get_con(self):
        if not self._connection_pool:
            await self.connect()
            return 0
        else:
            conn = await self._connection_pool.acquire()
            return conn

    async def release_con(self, conn):
        await self._connection_pool.release(conn)

    # because always get error, so im bring node model to here
    async def node_trans(self, idn: int, ids: int, query: str):
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                valid = True
                check_node = await self.con.execute(query=f"select type from \"hardware\" where id_hardware='{idn}' and type!='sensor';")
                if check_node == 'SELECT 1':
                    for i in ids:
                        res = await self.con.execute(query=f"select type from \"hardware\" where id_hardware='{i}' and type='sensor';")
                        if res != 'SELECT 1':
                            print('not sensor type')
                            valid = False
                            break
                else:
                    valid = False
                if valid:
                    res = await self.con.execute(query)
                    print('Success',res)
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)
                
@lru_cache()
def database_instance():
    return Database()