from django.urls import path
from django.urls import include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.utils.logger import get_logger

logger = get_logger()

@api_view(http_method_names=["GET"])
@permission_classes(permission_classes=[AllowAny])
def health_check(request):
    logger.info("health check")
    return Response(data={"msg": "health check ok"}, status=200)


urlpatterns = [
    path('auth/', include("custom_auth.urls")),
    path('blog/', include("blog.urls")),
    path('healthcheck', health_check),
]