from typing import Union, List, Dict
from pydantic import BaseModel




class SuccessResponse(BaseModel):
    ok: bool = True
    data: Union[List, Dict]

class SuccessCreatedResponse(SuccessResponse):
    data: dict = {"message": "created"}

class ErrorDetailResponse(BaseModel):
    error_code: str
    error_detail: str = ""
    errors: list = []


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetailResponse


class ClientResponse(BaseModel):
    name: str
    last_name: str
    phone: str
    age: str

class ClientFullResponse(SuccessResponse):
    data: ClientResponse

class ClientsFullResponse(SuccessResponse):
    data: List[ClientResponse]



