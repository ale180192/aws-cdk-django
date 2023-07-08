from rest_framework.serializers import Serializer
from rest_framework.serializers import EmailField
from rest_framework.serializers import CharField




class SignupRequestSerializer(Serializer):
    email = EmailField()
    password = CharField()
    name = CharField()