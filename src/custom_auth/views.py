import logging

from django.db import transaction, IntegrityError
from django.http import HttpRequest
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from custom_auth.serializers import SignupRequestSerializer
from custom_auth.models import CustomUser

from app.utils.logger import get_logger

logger = get_logger()


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def signup(request: HttpRequest):
    """
    This method create an user for the system if data is correct.
    The post request requires the following fields:
        name: Full name of the user (example: Jose Pérez Gómez).
        email: Valid email existing in the system.
        password: Valid password for sent email.
    :param request: The incoming request.
    :return: Return http response 201 if user is created successfully, or a 40X error otherwise.
    """
    logger.info("request data: ")
    logger.info(request.data)
    ser = SignupRequestSerializer(data=request.data)
    if not ser.is_valid(raise_exception=True):
        return Response(
            data={"error": "name, password and email are required to register a user."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            CustomUser.objects.create_user(
                name=ser.data["name"],
                password=ser.data["password"],
                email=ser.data["email"],
                is_active=True
            )
            

    except IntegrityError as e:
        print(str(e))
        msg = f"Email {ser.data['email']} already exist!"
        logger.warning(msg)
        return Response(
            {"error": msg},
            status=status.HTTP_409_CONFLICT
        )
    
    return Response(data={"msg": "ok"})

