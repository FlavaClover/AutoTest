from typing import List

from src.entities.language import LanguageFactory, Language
from src.entities.schemas import Solve, Test, TestResult
from src.db.database import DataBase


class SolveManager:
    @classmethod
    async def create(cls, solve: Solve):
        id_solve = await DataBase().insert('solves', solve.dict())
        solve.id = id_solve
        return solve

    @classmethod
    async def solve(cls, solve: Solve, tests: List[Test], language: str):
        test_results: List[bool] = list()
        count_ok = 0
        language = LanguageFactory().get_language(language)
        if language is None:
            solve.solve_status = 'language does not exists'
        else:
            for test in tests:
                test_result = await cls.solve_test(solve, test, language)
                if test_result.result:
                    count_ok += 1

                test_results.append(test_result.dict())

            solve.solve_status = 'bad' if count_ok != len(test_results) else 'ok'
            solve.count_ok_tests = count_ok

        await DataBase().update('solves', where='id = :id', values=solve.dict())

        await DataBase().insert_many('solve_tests', values=test_results)

    @classmethod
    async def solve_test(cls, solve, test: Test, language: Language) -> TestResult:
        test_result = TestResult(result=None, expected=test.output_file, input=test.input_file, actual=None,
                                 id_solve=solve.id)

        output_actual = language.run(solve.code, test.input_file)
        if output_actual is None:
            test_result.result = False
            test_result.comment = 'Runtime error'
        else:
            test_result.actual = output_actual
            test_result.result = test_result.expected.decode().strip('\n') == test_result.actual.decode().strip('\n')

        return test_result

    @classmethod
    async def get_by_user(cls, id_user: int):
        data = await DataBase().select('solves', where='id_user = :id_user', params={'id_user': id_user})
        if data is None:
            return []
        return list(map(lambda x: Solve(**x), data))

    @classmethod
    async def get_solve_tests(cls, id_solve: int):
        data = await DataBase().select('solve_tests', where='id_solve = :id_solve',
                                       params={'id_solve': id_solve})

        return list(map(lambda x: TestResult(**x), data))

    @classmethod
    async def get_solve_by_id(cls, id_solve: int):
        data = await DataBase().select('solves', where='id = :id', params={'id': id_solve}, scalar=True)

        if data is None:
            return None
        else:
            return Solve(**data)

    @classmethod
    async def get_solve_by_problem(cls, id_problem: int):
        data = await DataBase().select('solves', where='id_problem = :id', params={'id': id_problem})

        return list(map(lambda x: Solve(**x), data))

    @classmethod
    async def get_solve_by_problem_user(cls, id_problem: int, id_user: int):
        data = await DataBase().select('solves', where='id_problem = :id_problem and id_user = :id_user',
                                       params={'id_problem': id_problem, 'id_user': id_user})

        return list(map(lambda x: Solve(**x), data))
