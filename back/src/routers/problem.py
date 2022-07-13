from fastapi import APIRouter, HTTPException, status, File, Response, Depends
from src.entities.problem import ProblemManager, Problem, Test
from src.entities.user import User
from src.tools.pg_catch_error_decorator import pg_catch_error_decorator
import io
from typing import List
import subprocess

router = APIRouter()


@router.post('/create')
@pg_catch_error_decorator
async def create(problem: Problem, _: User = Depends()):
    return await ProblemManager.create(problem)


@router.get('/get/{id_problem}', response_model=Problem)
@pg_catch_error_decorator
async def get(id_problem: int, _: User = Depends()):
    problem = await ProblemManager.get(id_problem)
    if problem is None:
        raise HTTPException(detail='Problem does not exists', status_code=status.HTTP_404_NOT_FOUND)
    else:
        return problem


@router.get('/all', response_model=List[Problem])
@pg_catch_error_decorator
async def get_all(_: User = Depends()):
    return await ProblemManager.get_all()


@router.post('/create_test/{id_problem}')
@pg_catch_error_decorator
async def create_test(id_problem: int, input_file: bytes = File(), output_file: bytes = File(), _: User = Depends()):
    await ProblemManager.create_test(Test(id_problem=id_problem, input_file=input_file, output_file=output_file))
    return Response(status_code=200)


@router.get('/tests/{id_problem}', response_model=List[Test])
@pg_catch_error_decorator
async def get_tests(id_problem: int, _: User = Depends()):
    return await ProblemManager.get_tests(id_problem)


@router.post('/testing/{id_problem}')
@pg_catch_error_decorator
async def testing(id_problem: int, code: bytes = File(), user: User = Depends()):
    tests = await ProblemManager.get_tests(id_problem)

    test_result: List[bool] = list()
    for test in tests:
        output_actual = subprocess.check_output(['python3.10', '-c', code.decode()], input=test.input_file)

        output_actual = output_actual.decode().strip('\n')
        output_expect = test.output_file.decode().strip('\n')

        test_result.append({
            'result': output_expect == output_actual,
            'expected': output_expect,
            'actual': output_actual,
            'input': test.input_file.decode()
        })

    return test_result
