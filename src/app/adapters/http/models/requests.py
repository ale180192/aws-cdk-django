from pydantic import BaseModel, Field, validator




class NameModel(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)

class ClientRequest(BaseModel):
    client_name: NameModel
    phone: str = Field(..., min_length=10, max_length=10)
    age: int = Field(..., gt=18)

    class Config:
        schema_extra = {
            "example": {
                "client_name": {
                    "name": "Juan",
                    "last_name": "López"
                },
                "phone": "5555555555",
                "age": 30
            }
        }

    @validator('phone')
    def validate_phone(cls, phone):
        if len(phone) != 10:
            raise ValueError('El número de teléfono debe tener 10 dígitos')
        return phone

    @validator('age')
    def validate_age(cls, age):
        if age <= 18:
            raise ValueError('La edad debe ser mayor que 18')
        return age