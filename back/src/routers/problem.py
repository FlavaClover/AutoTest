from fastapi import APIRouter, HTTPException, status, File, Response, Depends, BackgroundTasks
from src.entities.problem import ProblemManager
from src.entities.solve import SolveManager
from src.entities.schemas import User, Problem, Test, Solve, SolveStatus, UserProblem
from src.tools.pg_catch_error_decorator import pg_catch_error_decorator
import io
from typing import List
import subprocess
import asyncio

router = APIRouter()


@router.post('/create')
@pg_catch_error_decorator
async def create(problem: Problem, _: User = Depends()):
    return await ProblemManager.create(problem)


@router.get('/{id_problem}', response_model=UserProblem)
@pg_catch_error_decorator
async def get(id_problem: int, user: User = Depends()):
    problem = await ProblemManager.get(id_problem)
    if problem is None:
        raise HTTPException(detail='Problem does not exists', status_code=status.HTTP_404_NOT_FOUND)

    solves = await SolveManager.get_solve_by_problem_user(problem.id, user.id)
    return UserProblem(solves=solves, **problem.dict())


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
async def testing(id_problem: int, language: str,
                  background_tasks: BackgroundTasks, code: bytes = File(), user: User = Depends()):
    solve = await SolveManager.create(Solve(id_problem=id_problem, id_user=user.id,
                                            solve_status='running', code=code, language=language))

    tests = await ProblemManager.get_tests(id_problem)

    background_tasks.add_task(SolveManager().solve, solve, tests, language)

    return solve
