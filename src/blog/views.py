import logging
import requests

from django.http import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from blog.models import Post, Comments
from blog.serializers import PostSerializer

logger = logging.getLogger(__name__)



class BlogViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def retrieve_data_blog(request: HttpRequest):
    posts_url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url=posts_url)
    posts = response.json()
    posts_obj = [
        Post(
            id=post["id"],
            user_id=post["userId"],
            title=post["title"],
            body=post["body"]
        ) for post in posts
    ]
    posts_created = Post.objects.bulk_create(posts_obj, ignore_conflicts=True)
    
    # load comments for each post
    for post in posts_created:
        url = f"https://jsonplaceholder.typicode.com/posts/{post.id}/comments"
        response = requests.get(url=url)
        comments = response.json()
        comments_obj = [
            Comments(
                id=comment["id"],
                name=comment["name"],
                email=comment["email"],
                body=comment["body"],
                post=post
            ) for comment in comments
        ]
        Comments.objects.bulk_create(comments_obj, ignore_conflicts=True)
    
    
    return Response(data={"total_posts": len(posts_created)})