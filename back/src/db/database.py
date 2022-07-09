import configparser
from typing import List
import logging
import databases


config = configparser.ConfigParser()
config.read('configs/config.ini')


DATABASE_URL = f"postgresql://{config['Database']['user']}:{config['Database']['pwd']}@" \
               f"{config['Database']['host']}/{config['Database']['db']}"

database = databases.Database(DATABASE_URL)

logger = logging.getLogger('database')


class DataBase:
    @classmethod
    async def select(cls, table: str, where: str = None, columns: List[str] = None):
        sql = 'SELECT ' + (', '.join(columns) if columns is not None else '* ') + 'FROM ' + table
        if where is not None:
            sql += ' WHERE ' + where
        try:
            data = await database.fetch_all(query=sql)
        except Exception as e:
            logger.info('Executed: ', extra={'sql': sql, 'result': str(e)})
            data = None
        else:
            logger.info('Executed: ', extra={'sql': sql, 'result': data})

        return data

    @classmethod
    @database.transaction()
    async def function(cls, name: str, fetch_one=True, **params):
        sql = 'SELECT * FROM ' + name + '(' + ', '.join(map(lambda x: ':' + x, params.keys())) + ')'

        try:
            if fetch_one:
                data = await database.fetch_one(query=sql, values=params)
            else:
                data = await database.fetch_all(query=sql, values=params)
        except Exception as e:
            logger.info('Executed: ', extra={'sql': sql, 'result': str(e)})
            data = None
        else:
            logger.info('Executed: ', extra={'sql': sql, 'result': data})

        return data
