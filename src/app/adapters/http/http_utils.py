from .models.responses import (
    SuccessResponse
)


def get_success_response(data: dict):
    response_model = SuccessResponse(data=data)
    return response_model