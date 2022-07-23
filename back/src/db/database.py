import configparser
from typing import List
import logging
import asyncpg.exceptions
import databases

logger = logging.getLogger('database')


class DataBase:
    @classmethod
    def set_settings(cls, database_url: str):
        cls._database = databases.Database(database_url)

    @classmethod
    async def select(cls, table: str, where: str = None, columns: List[str] = None, params: dict = None,
                     scalar=False):
        sql = 'SELECT ' + (', '.join(columns) if columns is not None else '* ') + 'FROM ' + table
        if where is not None:
            sql += ' WHERE ' + where

        logger.info('Executing: ', extra={'sql': sql, 'result': '...'})
        try:
            async with cls._database.transaction():
                if not scalar:
                    data = await cls._database.fetch_all(query=sql, values=params)
                else:
                    data = await cls._database.fetch_one(query=sql, values=params)

        except asyncpg.exceptions.PostgresError as e:
            logger.info('Executed: ', extra={'sql': sql, 'result': str(e)})
            raise e
        else:
            logger.info('Executed: ', extra={'sql': sql, 'result': data})

        return data

    @classmethod
    async def insert(cls, table: str, values: dict, remove_none=True):
        sql, values = cls.__obj_to_sql(table, values, remove_none=remove_none)

        logger.info('Executing:', extra={'sql': sql, 'result': '...'})
        try:
            async with cls._database.transaction():
                data = await cls._database.fetch_one(query=sql, values=values)
                id_obj = list(dict(data).values())[0]
        except asyncpg.exceptions.PostgresError as e:
            logger.info('Executed:', extra={'sql': sql, 'result': str(e)})
            raise e
        else:
            logger.info('Executed:', extra={'sql': sql, 'result': data})

            return id_obj

    @classmethod
    async def insert_many(cls, table: str, values: List[dict], remove_none=True):
        async with cls._database.transaction():
            for value in values:
                sql, value = cls.__obj_to_sql(table, value, remove_none=remove_none)
                logger.info('Executing:', extra={'sql': sql, 'result': '...'})
                try:
                    data = await cls._database.fetch_one(query=sql, values=value)
                except asyncpg.exceptions.PostgresError as e:
                    logger.info('Executed:', extra={'sql': sql, 'result': str(e)})
                    raise e
                else:
                    logger.info('Executed:', extra={'sql': sql, 'result': data})

    @classmethod
    async def update(cls, table: str, values: dict, where: str = None):
        sql = 'UPDATE ' + table + ' SET ' + ', '.join([str(i) + ' = :' + str(i) for i in values])
        if where is not None:
            sql += ' WHERE ' + where

        logger.info('Executing:', extra={'sql': sql, 'result': '...'})
        try:
            async with cls._database.transaction():
                data = await cls._database.execute(sql, values=values)
        except asyncpg.exceptions.PostgresError as e:
            logger.info('Executed:', extra={'sql': sql, 'result': str(e)})
            raise e
        else:
            logger.info('Executed:', extra={'sql': sql, 'result': data})

    @classmethod
    async def function(cls, name: str, fetch_one=True, **params):
        sql = 'SELECT * FROM ' + name + '(' + ', '.join(map(lambda x: ':' + x, params.keys())) + ')'

        logger.info('Executing:', extra={'sql': sql, 'result': '...'})
        try:
            if fetch_one:
                async with cls._database.transaction():
                    data = await cls._database.fetch_one(query=sql, values=params)
            else:
                async with cls._database.transaction():
                    data = await cls._database.fetch_all(query=sql, values=params)
        except asyncpg.exceptions.PostgresError as e:
            logger.info('Executed:', extra={'sql': sql, 'result': str(e)})
            raise e
        else:
            logger.info('Executed:', extra={'sql': sql, 'result': data})

        return data

    @classmethod
    async def connect(cls):
        await cls._database.connect()

    @classmethod
    async def disconnect(cls):
        await cls._database.disconnect()

    @staticmethod
    def __obj_to_sql(table, values, remove_none=True):
        if remove_none:
            values = {k: v for k, v in values.items() if v is not None}

        sql = 'INSERT INTO ' + table + '(' + ','.join(values.keys()) + ') VALUES (' \
              + ','.join(map(lambda x: ':' + x, values.keys())) + ') RETURNING id'

        return sql, values
