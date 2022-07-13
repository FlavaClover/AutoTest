from psycopg2.errors import UndefinedColumn, InvalidColumnReference, UndefinedTable, Error, InvalidTextRepresentation, \
    InFailedSqlTransaction
from fastapi import HTTPException, status
from functools import wraps
from asyncpg.exceptions import UndefinedColumnError, InvalidColumnReferenceError, UndefinedTableError, \
    PostgresSyntaxError, InFailedSQLTransactionError, NotNullViolationError, PostgresError


def pg_catch_error_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UndefinedColumnError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except InvalidColumnReferenceError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except UndefinedTableError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except PostgresSyntaxError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except InFailedSQLTransactionError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except NotNullViolationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except PostgresError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException as e:
            raise e

    return wrapper
