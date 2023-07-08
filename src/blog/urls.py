from django.urls import path

from blog import views

urlpatterns = [
    path('retrieve_data_blog', views.retrieve_data_blog, name='retrieve_data_blog'),
    path('posts', views.BlogViewSet.as_view({"get": "list"}), name='posts'),
]