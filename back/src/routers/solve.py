from fastapi import APIRouter, Depends, HTTPException, status
from src.entities.solve import SolveManager
from typing import List
from src.entities.schemas import Solve, User, SolveDetailed

router = APIRouter()


@router.get('/all', response_model=List[Solve])
async def get_all(user: User = Depends()):
    solves = await SolveManager().get_by_user(user.id)

    return solves


@router.get('/{id_solve}')
async def get_solve_info(id_solve: int, user: User = Depends()):
    solve = await SolveManager().get_solve_by_id(id_solve)
    if solve is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Solve does not exists')
    if solve.id_user != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not yours')

    tests = await SolveManager().get_solve_tests(id_solve)

    return SolveDetailed(solve=solve, tests=tests)