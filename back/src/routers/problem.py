from fastapi import APIRouter, HTTPException, status, File, Response, Depends
from src.entities.problem import ProblemManager, Problem, Test
from src.entities.user import User
from src.tools.pg_catch_error_decorator import pg_catch_error_decorator
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
    script_name = 'scripts/problem' + str(id_problem) + user.login + '.py'
    with open(script_name, 'wb') as source:
        source.write(code)

    test_result: List[bool] = list()
    for test in tests:

        test_input = script_name + '_input_test.txt'
        test_output = script_name + '_output_test.txt'
        test_output_actual = script_name + '_output_test_actual.txt'

        with open(test_input, 'wb') as inp:
            inp.write(test.input_file)

        with open(test_output, 'wb') as out:
            out.write(test.output_file)

        subprocess.Popen(['python3.10', script_name],
                         stdin=open(test_input, 'r'),
                         stdout=open(test_output_actual, 'wb')).wait()

        with open(test_output_actual, 'rb') as actual:
            data = actual.read().decode().strip('\n')
            if data == test.output_file.decode().strip('\n'):
                test_result.append(True)
            else:
                test_result.append(False)

    return test_result
