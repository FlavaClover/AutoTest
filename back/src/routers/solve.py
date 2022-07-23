from fastapi import APIRouter, Depends
from src.entities.solve import SolveManager
from typing import List
from src.entities.schemas import Solve, User

router = APIRouter()


@router.get('/all', response_model=List[Solve])
async def get_all(user: User = Depends()):
    solves = SolveManager().get_by_user(user.id)

    return solves

