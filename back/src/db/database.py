import configparser
from typing import List

import databases


config = configparser.ConfigParser()
config.read('configs/config.ini')


DATABASE_URL = f"postgresql://{config['Database']['user']}:{config['Database']['pwd']}@" \
               f"{config['Database']['host']}/{config['Database']['db']}"

database = databases.Database(DATABASE_URL)


class DataBase:
    def __init__(self):
        pass

    @classmethod
    async def select(cls, table: str, where: str = None, columns: List[str] = None):
        sql = 'SELECT ' + (', '.join(columns) if columns is not None else '*') + 'FROM ' + table

        return await database.fetch_all(query=sql)

    @classmethod
    @database.transaction()
    async def function(cls, name: str, **params):
        sql = 'SELECT * FROM ' + name + '(' + ', '.join(map(lambda x: ':' + x, params.keys())) + ')'

        print(sql)
        return await database.fetch_one(query=sql, values=params)
