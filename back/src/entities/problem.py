from src.db.database import DataBase
from src.entities.schemas import Problem, Test


class ProblemManager:
    @classmethod
    async def create(cls, problem: Problem):
        id_problem = await DataBase.insert('problems', problem.dict())
        return id_problem

    @classmethod
    async def get(cls, id_problem: int):
        data = await DataBase.select('problems', where='id = :id', params={'id': id_problem}, scalar=True)
        return data if data is None else Problem(**data)

    @classmethod
    async def get_all(cls):
        data = await DataBase.select('problems')

        data = list(map(lambda x: Problem(**x), data))

        return data

    @classmethod
    async def create_test(cls, test: Test):
        await DataBase.insert('problems_tests', test.dict())

    @classmethod
    async def get_tests(cls, id_problem: int):
        data = await DataBase.select('problems_tests', where='id_problem = :id', params={'id': id_problem})
        data = list(map(lambda x: Test(**x), data))

        return data
