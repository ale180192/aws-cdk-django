from django.urls import path
from django.urls import include

from app.utils.logger import get_logger

logger = get_logger()


urlpatterns = [
    path('auth/', include("custom_auth.urls")),
    path('blog/', include("blog.urls")),
]