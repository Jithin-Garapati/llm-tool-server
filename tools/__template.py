from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Define input structure (you can define as many inputs as you want)
class Input(BaseModel):
    input1: str                          # required input and must be a string
    input2: Optional[int] = None         # optional input and must be an integer
    input3: Optional[List[str]] = None   # optional list input and must be a list of strings

# Define output structure (you can define as many outputs as you want)
class Output(BaseModel):
    output1: str                         # output and must be a string
    output2: str                         # output and must be a string
    output3: int                         # output and must be an integer

# Define your tool endpoint
@router.post("/")
def your_function_name(data: Input) -> Output:
    # Write your function here
    # Access inputs like: data.input1, data.input2, data.input3
    

    return Output(
        output1="",
        output2="",
        output3=0
    )
