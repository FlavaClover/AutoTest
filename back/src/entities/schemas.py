import datetime
from typing import Optional, Union, List
from enum import Enum
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int]
    login: str
    pwd: str
    salt: Optional[str]
    last_login: Optional[datetime.datetime]


class Problem(BaseModel):
    id: Optional[int]
    task: str
    input_desc: str
    output_desc: str


class Test(BaseModel):
    id: Optional[int]
    id_problem: Union[int, Problem]
    input_file: bytes
    output_file: bytes


class SolveStatus(Enum):
    RUNNING = 'running'
    BAD = 'bad'
    OK = 'ok'


class Solve(BaseModel):
    id: Optional[int]
    id_problem: int
    id_user: int
    code: bytes
    count_ok_tests: int = 0
    solve_status: str
    language: str


class TestResult(BaseModel):
    id_solve: int
    result: Optional[Union[bool, str]]
    actual: Optional[bytes]
    expected: bytes
    input: bytes
    comment: Optional[str]


class SolveDetailed(BaseModel):
    solve: Solve
    tests: List[TestResult]


class UserProblem(Problem):
    solves: List[Solve]
